import { NextRequest, NextResponse } from 'next/server';
import { GoogleGenerativeAI } from '@google/generative-ai';

// Initialize Google Generative AI
const genAI = new GoogleGenerativeAI(process.env.GOOGLE_GENAI_API_KEY || '');

export async function POST(request: NextRequest) {
  try {
    const { image, mimeType } = await request.json();

    if (!image) {
      return NextResponse.json(
        { error: 'No image provided' },
        { status: 400 }
      );
    }

    // Initialize Gemini Vision model
    const model = genAI.getGenerativeModel({ model: 'gemini-2.0-flash-exp' });

    // Convert base64 to Uint8Array
    const imageData = Uint8Array.from(atob(image), c => c.charCodeAt(0));

    // Create image part
    const imagePart = {
      inlineData: {
        data: image,
        mimeType: mimeType || 'image/jpeg'
      }
    };

    // Analyze the image
    const prompt = `
    Analyze this image and provide information about what you see. Focus on:
    1. What type of event or situation is shown (accident, traffic, construction, event, etc.)
    2. What is happening in the image
    3. Any relevant details about location, severity, or impact
    
    Return your analysis in a structured format that can help categorize this as a city event.
    Be specific about what you observe and suggest an appropriate event type.
    `;

    const result = await model.generateContent([prompt, imagePart]);
    const response = await result.response;
    const analysis = response.text();

    // Extract suggested event type from analysis
    let suggestedType = 'other';
    const analysisLower = analysis.toLowerCase();
    
    if (analysisLower.includes('accident') || analysisLower.includes('crash') || analysisLower.includes('collision')) {
      suggestedType = 'accident';
    } else if (analysisLower.includes('traffic') || analysisLower.includes('congestion') || analysisLower.includes('jam')) {
      suggestedType = 'traffic';
    } else if (analysisLower.includes('construction') || analysisLower.includes('road work') || analysisLower.includes('maintenance')) {
      suggestedType = 'construction';
    } else if (analysisLower.includes('event') || analysisLower.includes('festival') || analysisLower.includes('gathering')) {
      suggestedType = 'event';
    }

    // Generate suggested title and description
    const titlePrompt = `Based on this analysis: "${analysis}", generate a brief, concise title (max 10 words) for this event.`;
    const titleResult = await model.generateContent(titlePrompt);
    const suggestedTitle = (await titleResult.response).text().replace(/"/g, '').trim();

    const descPrompt = `Based on this analysis: "${analysis}", generate a detailed description (2-3 sentences) of what happened.`;
    const descResult = await model.generateContent(descPrompt);
    const suggestedDescription = (await descResult.response).text().replace(/"/g, '').trim();

    return NextResponse.json({
      analysis,
      suggestedType,
      suggestedTitle,
      suggestedDescription
    });

  } catch (error) {
    console.error('Error analyzing image:', error);
    return NextResponse.json(
      { error: 'Failed to analyze image' },
      { status: 500 }
    );
  }
} 