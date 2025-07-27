"use client";
import { useState } from "react";
import { Globe, ChevronDown } from "lucide-react";
import { Button } from "@/components/ui/button";

interface Language {
  code: string;
  name: string;
  nativeName: string;
}

const languages: Language[] = [
  { code: "en", name: "English", nativeName: "English" },
  { code: "es", name: "Spanish", nativeName: "Español" },
  { code: "fr", name: "French", nativeName: "Français" },
  { code: "de", name: "German", nativeName: "Deutsch" },
  { code: "it", name: "Italian", nativeName: "Italiano" },
  { code: "pt", name: "Portuguese", nativeName: "Português" },
  { code: "ru", name: "Russian", nativeName: "Русский" },
  { code: "zh", name: "Chinese", nativeName: "中文" },
  { code: "ja", name: "Japanese", nativeName: "日本語" },
  { code: "ko", name: "Korean", nativeName: "한국어" },
  { code: "ar", name: "Arabic", nativeName: "العربية" },
  { code: "hi", name: "Hindi", nativeName: "हिन्दी" },
  { code: "th", name: "Thai", nativeName: "ไทย" },
  { code: "vi", name: "Vietnamese", nativeName: "Tiếng Việt" },
  { code: "id", name: "Indonesian", nativeName: "Bahasa Indonesia" },
  { code: "ms", name: "Malay", nativeName: "Bahasa Melayu" },
  { code: "tl", name: "Filipino", nativeName: "Filipino" },
  { code: "bn", name: "Bengali", nativeName: "বাংলা" },
  { code: "ur", name: "Urdu", nativeName: "اردو" },
  { code: "fa", name: "Persian", nativeName: "فارسی" },
  { code: "he", name: "Hebrew", nativeName: "עברית" },
  { code: "tr", name: "Turkish", nativeName: "Türkçe" },
  { code: "pl", name: "Polish", nativeName: "Polski" },
  { code: "nl", name: "Dutch", nativeName: "Nederlands" },
  { code: "sv", name: "Swedish", nativeName: "Svenska" },
  { code: "no", name: "Norwegian", nativeName: "Norsk" },
  { code: "da", name: "Danish", nativeName: "Dansk" },
  { code: "fi", name: "Finnish", nativeName: "Suomi" },
];

interface LanguageSelectorProps {
  selectedLanguage: string;
  onLanguageChange: (languageCode: string) => void;
  isDarkMode: boolean;
}

export default function LanguageSelector({ 
  selectedLanguage, 
  onLanguageChange, 
  isDarkMode 
}: LanguageSelectorProps) {
  const [isOpen, setIsOpen] = useState(false);
  
  const selectedLang = languages.find(lang => lang.code === selectedLanguage) || languages[0];

  return (
    <div className="relative">
      <Button
        variant="ghost"
        size="sm"
        onClick={() => setIsOpen(!isOpen)}
        className={`flex items-center space-x-2 px-3 py-2 rounded-lg transition-all duration-200 ${
          isDarkMode 
            ? "text-gray-300 hover:text-white hover:bg-gray-700/50" 
            : "text-gray-600 hover:text-gray-900 hover:bg-gray-100"
        }`}
      >
        <Globe className="w-4 h-4" />
        <span className="text-sm font-medium">{selectedLang.nativeName}</span>
        <ChevronDown className={`w-4 h-4 transition-transform duration-200 ${isOpen ? "rotate-180" : ""}`} />
      </Button>

      {isOpen && (
        <div className={`absolute top-full left-0 mt-1 w-64 max-h-60 overflow-y-auto rounded-lg shadow-lg border z-50 ${
          isDarkMode 
            ? "bg-gray-800 border-gray-600" 
            : "bg-white border-gray-200"
        }`}>
          {languages.map((language) => (
            <button
              key={language.code}
              onClick={() => {
                onLanguageChange(language.code);
                setIsOpen(false);
              }}
              className={`w-full text-left px-4 py-3 hover:bg-opacity-80 transition-colors duration-150 ${
                language.code === selectedLanguage
                  ? isDarkMode 
                    ? "bg-blue-600 text-white" 
                    : "bg-blue-50 text-blue-700"
                  : isDarkMode 
                    ? "text-gray-300 hover:bg-gray-700" 
                    : "text-gray-700 hover:bg-gray-50"
              }`}
            >
              <div className="flex flex-col">
                <span className="font-medium">{language.nativeName}</span>
                {language.nativeName !== language.name && (
                  <span className={`text-xs ${
                    language.code === selectedLanguage
                      ? isDarkMode ? "text-blue-200" : "text-blue-600"
                      : isDarkMode ? "text-gray-400" : "text-gray-500"
                  }`}>
                    {language.name}
                  </span>
                )}
              </div>
            </button>
          ))}
        </div>
      )}
    </div>
  );
} 