export interface UserProfile {
  displayName: string;
  email: string;
  createdAt: number;
}

export interface Person {
  id: string;
  name: string;
  birthDate: string;   // "YYYY-MM-DD"
  birthTime: string;   // "HH:MM"
  birthPlace: string;
  isSelf: boolean;     // true = kullanıcının kendisi
  createdAt: number;
}

export interface PersonFormData {
  name: string;
  birthDate: string;
  birthTime: string;
  birthPlace: string;
  isSelf?: boolean;
}
