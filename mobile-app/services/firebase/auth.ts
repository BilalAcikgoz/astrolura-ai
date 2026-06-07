import {
  signInWithEmailAndPassword,
  createUserWithEmailAndPassword,
  signOut,
  onAuthStateChanged,
  User,
  updateProfile,
  GoogleAuthProvider,
  signInWithCredential,
} from 'firebase/auth';
import { getAuth } from '../../firebase.config';

export async function loginWithEmail(email: string, password: string) {
  return signInWithEmailAndPassword(getAuth(), email, password);
}

export async function registerWithEmail(email: string, password: string, displayName: string) {
  const credential = await createUserWithEmailAndPassword(getAuth(), email, password);
  await updateProfile(credential.user, { displayName });
  return credential;
}

export async function logout() {
  return signOut(getAuth());
}

export function onAuthChange(callback: (user: User | null) => void) {
  return onAuthStateChanged(getAuth(), callback);
}

export async function signInWithGoogleCredential(idToken: string) {
  const credential = GoogleAuthProvider.credential(idToken);
  return signInWithCredential(getAuth(), credential);
}
