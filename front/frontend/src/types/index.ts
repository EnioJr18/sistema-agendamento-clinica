// Types based on Django models

export interface Usuario {
  id: number;
  first_name: string;
  last_name: string;
  username: string;
  tipo: 'MEDICO' | 'PACIENTE' | 'ADMIN';
  email: string;
  telefone: string;
  data_nascimento?: string | null;
  idade?: number | null;
}

export interface LoginCredentials {
  username: string;
  password: string;
}

export interface AuthTokens {
  access: string;
  refresh: string;
}

export interface RegisterUserData {
  username: string;
  first_name: string;
  last_name: string;
  email: string;
  password: string;
  tipo?: Usuario['tipo'];
  telefone?: string | null;
  data_nascimento?: string | null;
}

export interface Medico {
  id: number;
  usuario: number;
  nome: string;
  especialidade: string;
  crm: string;
  email: string;
  telefone: string;
  disponibilidade: string;
  ativo: boolean;
}

export interface Agendamento {
  id: number;
  medico: number;
  nome_medico?: string;
  especialidade_medico?: string;
  paciente: number;
  nome_paciente?: string;
  email_paciente?: string;
  telefone_paciente?: string;
  idade_paciente?: number | null;
  data_horario: string;
  status: 'AGENDADO' | 'CANCELADO' | 'CONCLUIDO';
  criado_em: string;
}

export interface CreateSchedullingData {
  medico: number;
  data_horario: string;
  status?: Agendamento['status'];
}
