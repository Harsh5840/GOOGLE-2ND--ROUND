// Import the functions you need from the SDKs you need
import { initializeApp } from "firebase/app";
import { getAuth } from "firebase/auth";
import { getFirestore } from "firebase/firestore";
// TODO: Add SDKs for Firebase products that you want to use
// https://firebase.google.com/docs/web/setup#available-libraries

// Your web app's Firebase configuration
// For Firebase JS SDK v7.20.0 and later, measurementId is optional
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
const app = initializeApp(firebaseConfig);
const auth = getAuth(app);
const db = getFirestore(app);

export { app, auth, db };