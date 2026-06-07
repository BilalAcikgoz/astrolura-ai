import { useState, useEffect, useCallback } from 'react';
import { useAuth } from '../context/AuthContext';
import { getPersons, addPerson, deletePerson, updatePerson } from '../services/firebase/persons';
import { Person, PersonFormData } from '../types/person.types';

export function usePersons() {
  const { user } = useAuth();
  const [persons, setPersons] = useState<Person[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchPersons = useCallback(async () => {
    if (!user) return;
    setLoading(true);
    setError(null);
    try {
      const data = await getPersons(user.uid);
      setPersons(data);
    } catch {
      setError('Kişiler yüklenemedi.');
    } finally {
      setLoading(false);
    }
  }, [user]);

  useEffect(() => {
    fetchPersons();
  }, [fetchPersons]);

  async function createPerson(data: PersonFormData): Promise<Person | null> {
    if (!user) return null;
    try {
      const p = await addPerson(user.uid, data);
      setPersons((prev) => [p, ...prev]);
      return p;
    } catch {
      setError('Kişi eklenemedi.');
      return null;
    }
  }

  async function editPerson(personId: string, data: Partial<PersonFormData>) {
    if (!user) return;
    await updatePerson(user.uid, personId, data);
    setPersons((prev) =>
      prev.map((p) => (p.id === personId ? { ...p, ...data } : p))
    );
  }

  async function removePerson(personId: string) {
    if (!user) return;
    await deletePerson(user.uid, personId);
    setPersons((prev) => prev.filter((p) => p.id !== personId));
  }

  return { persons, loading, error, fetchPersons, createPerson, editPerson, removePerson };
}
