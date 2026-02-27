// Types based on Django models

export interface Usuario {
  id: number;
  first_name: string;
  last_name: string;
  username: string;
  tipo: 'MEDICO' | 'PACIENTE' | 'ADMIN';
  email: string;
  telefone: string;
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
  medico_nome?: string;
  medico_especialidade?: string;
  paciente: number;
  data_horario: string;
  status: 'AGENDADO' | 'CANCELADO' | 'CONCLUIDO';
  criado_em: string;
}
