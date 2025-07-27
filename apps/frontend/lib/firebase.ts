// Import the functions you need from the SDKs you need
import { initializeApp } from "firebase/app";
import { getAuth } from "firebase/auth";
import { getFirestore } from "firebase/firestore";
// TODO: Add SDKs for Firebase products that you want to use
// https://firebase.google.com/docs/web/setup#available-libraries

// Your web app's Firebase configuration
const firebaseConfig = {
  apiKey: "AIzaSyAbjrj9QScVJkFAt7J33B3WpakOHK2omTk",
  authDomain: "city-project-466410.firebaseapp.com",
  projectId: "city-project-466410",
  storageBucket: "city-project-466410.firebasestorage.app",
  messagingSenderId: "303784709433",
  appId: "1:303784709433:web:e578345206b3c899f32ce8"
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);
const auth = getAuth(app);
const db = getFirestore(app);

export { app, auth, db };