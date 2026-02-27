import { motion } from 'framer-motion';
import {
  Phone,
  Email,
  LocationOn,
  Facebook,
  Instagram,
  Twitter,
  LocalHospital,
} from '@mui/icons-material';
import { Divider } from '@mui/material';

export default function Footer() {
  const contactInfo = [
    { icon: <Phone />, text: '(11) 1234-5678', label: 'Telefone' },
    { icon: <Email />, text: 'contato@clinab.com.br', label: 'Email' },
    { icon: <LocationOn />, text: 'São Paulo, SP', label: 'Localização' },
  ];

  const socialLinks = [
    { icon: <Facebook />, label: 'Facebook', href: '#' },
    { icon: <Instagram />, label: 'Instagram', href: '#' },
    { icon: <Twitter />, label: 'Twitter', href: '#' },
  ];

  return (
    <footer className="bg-linear-to-r from-teal-700 to-cyan-700 text-white mt-auto">
      <div className="max-w-7xl mx-auto px-4 py-12">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {/* Logo e Descrição */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
            viewport={{ once: true }}
            className="space-y-4"
          >
            <div className="flex items-center gap-2">
              <LocalHospital className="text-4xl" />
              <div>
                <h3 className="text-2xl font-bold">CLINAB</h3>
                <p className="text-sm opacity-90">Cuidando da sua saúde</p>
              </div>
            </div>
            <p className="text-sm opacity-80 leading-relaxed">
              Excelência em atendimento médico com tecnologia de ponta e
              profissionais qualificados para cuidar de você e sua família.
            </p>
          </motion.div>

          {/* Informações de Contato */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.1 }}
            viewport={{ once: true }}
            className="space-y-4"
          >
            <h4 className="text-lg font-semibold mb-4">Contato</h4>
            {contactInfo.map((item, index) => (
              <div key={index} className="flex items-center gap-3 text-sm">
                <span className="opacity-80">{item.icon}</span>
                <div>
                  <p className="opacity-90">{item.text}</p>
                </div>
              </div>
            ))}
          </motion.div>

          {/* Redes Sociais */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.2 }}
            viewport={{ once: true }}
            className="space-y-4"
          >
            <h4 className="text-lg font-semibold mb-4">Redes Sociais</h4>
            <div className="flex gap-4">
              {socialLinks.map((social, index) => (
                <motion.a
                  key={index}
                  href={social.href}
                  aria-label={social.label}
                  whileHover={{ scale: 1.2, rotate: 5 }}
                  whileTap={{ scale: 0.9 }}
                  className="w-10 h-10 flex items-center justify-center rounded-full bg-white/10 hover:bg-white/20 transition-all duration-300"
                >
                  {social.icon}
                </motion.a>
              ))}
            </div>
            <div className="pt-4">
              <p className="text-sm opacity-80">
                <strong>Horário de Atendimento:</strong>
                <br />
                Seg - Sex: 8h às 18h
                <br />
                Sáb: 8h às 12h
              </p>
            </div>
          </motion.div>
        </div>

        <Divider className="my-8 bg-white/20" />

        <motion.div
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          transition={{ duration: 0.5, delay: 0.3 }}
          viewport={{ once: true }}
          className="text-center text-sm opacity-80"
        >
          <p>
            © {new Date().getFullYear()} CLINAB - Clínica Médica. Todos os
            direitos reservados.
          </p>
        </motion.div>
      </div>
    </footer>
  );
}
