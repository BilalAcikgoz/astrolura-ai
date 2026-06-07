import {
  collection,
  addDoc,
  updateDoc,
  deleteDoc,
  getDocs,
  doc,
  query,
  orderBy,
} from 'firebase/firestore';
import { db } from '../../firebase.config';
import { Person, PersonFormData } from '../../types/person.types';

function personsRef(uid: string) {
  return collection(db, 'users', uid, 'persons');
}

export async function getPersons(uid: string): Promise<Person[]> {
  const q = query(personsRef(uid), orderBy('createdAt', 'desc'));
  const snap = await getDocs(q);
  return snap.docs.map((d) => ({ id: d.id, ...d.data() } as Person));
}

export async function addPerson(uid: string, data: PersonFormData): Promise<Person> {
  const payload = {
    name: data.name,
    birthDate: data.birthDate,
    birthTime: data.birthTime,
    birthPlace: data.birthPlace,
    isSelf: data.isSelf ?? false,
    createdAt: Date.now(),
  };
  const ref = await addDoc(personsRef(uid), payload);
  return { id: ref.id, ...payload };
}

export async function updatePerson(uid: string, personId: string, data: Partial<PersonFormData>) {
  const ref = doc(db, 'users', uid, 'persons', personId);
  await updateDoc(ref, data as Record<string, unknown>);
}

export async function deletePerson(uid: string, personId: string) {
  const ref = doc(db, 'users', uid, 'persons', personId);
  await deleteDoc(ref);
}
