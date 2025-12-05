import { initializeApp } from "firebase/app";
import { getAuth } from "firebase/auth";

const firebaseConfig = {
  apiKey: "AIzaSyDQdolafbTnlNbk_klgC0aEf0KxyyTgHZs",
  authDomain: "handout-vault.firebaseapp.com",
  projectId: "handout-vault",
  storageBucket: "handout-vault.firebasestorage.app",
  messagingSenderId: "651020261690",
  appId: "1:651020261690:web:6f6820c8ef8328f3231803"
};

const app = initializeApp(firebaseConfig);

export const auth = getAuth(app);
export default app;
