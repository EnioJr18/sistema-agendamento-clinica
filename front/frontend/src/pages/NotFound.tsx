import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Button } from '@mui/material';
import { Home, ErrorOutline } from '@mui/icons-material';

export default function NotFound() {
  return (
    <div className="flex items-center justify-center min-h-[60vh]">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="text-center space-y-6 max-w-md"
      >
        <motion.div
          initial={{ scale: 0 }}
          animate={{ scale: 1 }}
          transition={{ duration: 0.5, delay: 0.2 }}
          className="flex justify-center"
        >
          <div className="w-32 h-32 bg-linear-to-r from-teal-600 to-cyan-600 rounded-full flex items-center justify-center">
            <ErrorOutline className="text-white text-7xl" />
          </div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.5, delay: 0.4 }}
          className="space-y-3"
        >
          <h1 className="text-6xl font-bold bg-linear-to-r from-teal-600 to-cyan-600 bg-clip-text text-transparent">
            404
          </h1>
          <h2 className="text-2xl font-semibold text-gray-800">
            Página não encontrada
          </h2>
          <p className="text-lg text-gray-600">
            A página que você está procurando não existe ou foi movida.
          </p>
        </motion.div>

        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.5, delay: 0.6 }}
        >
          <Button
            component={Link}
            to="/"
            variant="contained"
            size="large"
            startIcon={<Home />}
            className="bg-linear-to-r from-teal-600 to-cyan-600 hover:from-teal-700 hover:to-cyan-700 px-8 py-3"
          >
            Voltar para Home
          </Button>
        </motion.div>
      </motion.div>
    </div>
  );
}
