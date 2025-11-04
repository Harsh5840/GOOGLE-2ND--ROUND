// Import the functions you need from the SDKs you need
import { initializeApp } from "firebase/app";
import { getAnalytics } from "firebase/analytics";
import { getAuth } from "firebase/auth";
import { getFirestore } from "firebase/firestore";

// Your web app's Firebase configuration
const firebaseConfig = {
  apiKey: "AIzaSyBpnW9OuhyfCKC9x8ky8uKHkXsPA9YzBYQ",
  authDomain: "causal-galaxy-415009.firebaseapp.com",
  projectId: "causal-galaxy-415009",
  storageBucket: "causal-galaxy-415009.firebasestorage.app",
  messagingSenderId: "822987556610",
  appId: "1:822987556610:web:45a6413036f86d64b6e41b",
  measurementId: "G-TH1S24RY9E"
};

// Initialize Firebase
export const app = initializeApp(firebaseConfig);
export const auth = getAuth(app);
export const db = getFirestore(app);

// Initialize Analytics only on client side
export const analytics = typeof window !== 'undefined' ? getAnalytics(app) : null;