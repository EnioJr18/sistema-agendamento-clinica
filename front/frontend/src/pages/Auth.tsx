import { motion } from 'framer-motion';
import { Container } from '@mui/material';
import AuthCard from '../components/auth/AuthCard';

export default function Auth() {
  return (
    <div className="relative isolate overflow-hidden rounded-3xl bg-linear-to-br from-teal-50 via-white to-cyan-50 px-2 py-8 sm:px-4 sm:py-12">
      <div className="pointer-events-none absolute -top-16 -right-14 h-48 w-48 rounded-full bg-teal-200/50 blur-3xl" />
      <div className="pointer-events-none absolute -bottom-20 -left-14 h-52 w-52 rounded-full bg-cyan-200/50 blur-3xl" />

      <Container maxWidth="sm" className="relative z-10">
        <div className="space-y-6">
          <motion.div
            initial={{ opacity: 0, y: -16 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
            className="text-center space-y-3"
          >
            <h1 className="text-4xl sm:text-5xl font-black tracking-tight bg-linear-to-r from-teal-700 to-cyan-700 bg-clip-text text-transparent">
              Bem-vindo(a)
            </h1>
            <p className="text-slate-600 text-base sm:text-lg">
              Entre na sua conta ou crie um novo acesso em poucos segundos.
            </p>
          </motion.div>

          <AuthCard />

          <motion.p
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.5, delay: 0.2 }}
            className="text-center text-xs text-slate-500"
          >
            Ao continuar, você concorda em usar o sistema de agendamento com
            responsabilidade.
          </motion.p>
        </div>
      </Container>
    </div>
  );
}
