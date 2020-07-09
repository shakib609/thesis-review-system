/// <reference types="react-scripts" />

interface IUser {
  username: string;
  roles: { id: number; name: string }[];
  email: string;
  first_name: string;
  last_name: string;
  phone_number: string;
  profile_picture: null | string;
  cv_document: null | string;
  department: string;
}
