const { initializeApp } = require('firebase/app');
const { getAuth, signInAnonymously } = require('firebase/auth');

// We are going to test if your API Key is valid directly, completely bypassing Next.js!
const firebaseConfig = {
  apiKey: "AIzaSyCL1sZjUe_8GGm_V_aRC08clTr1bTZkkCM",
  authDomain: "gangu-adffd.firebaseapp.com",
  projectId: "gangu-adffd"
};

console.log("Initializing Firebase...");
const app = initializeApp(firebaseConfig);
const auth = getAuth(app);

console.log("Testing API Key...");
signInAnonymously(auth)
  .then(() => {
    console.log("✅ SUCCESS! The API Key is perfectly valid.");
    console.log("If Next.js is failing, it's a caching issue. Try deleting the .next folder!");
    process.exit(0);
  })
  .catch((error) => {
    console.log("❌ FAILED! Google Cloud rejected the API Key.");
    console.log("Error code:", error.code);
    console.log("Error message:", error.message);
    if (error.code === 'auth/api-key-not-valid') {
      console.log("\\n⚠️ This means your API key has been deleted or changed in Firebase!");
      console.log("Please go to Firebase Console -> Project Settings -> General, copy the NEW Web API Key, and update frontend/lib/firebase.ts!");
    }
    process.exit(1);
  });
