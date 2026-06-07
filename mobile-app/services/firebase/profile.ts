import { doc, setDoc, getDoc } from 'firebase/firestore';
import { User } from 'firebase/auth';
import { db } from '../../firebase.config';
import { UserProfile } from '../../types/person.types';

function userRef(uid: string) {
  return doc(db, 'users', uid);
}

// İlk girişte veya her auth state değişiminde çağrılır.
// merge:true sayesinde mevcut veriyi silmez, sadece eksik alanları doldurur.
export async function createUserProfile(user: User): Promise<void> {
  await setDoc(
    userRef(user.uid),
    {
      displayName: user.displayName || '',
      email: user.email || '',
      createdAt: Date.now(),
    },
    { merge: true }
  );
}

export async function getUserProfile(uid: string): Promise<UserProfile | null> {
  const snap = await getDoc(userRef(uid));
  return snap.exists() ? (snap.data() as UserProfile) : null;
}
