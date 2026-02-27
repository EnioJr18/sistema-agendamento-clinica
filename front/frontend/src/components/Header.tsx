import { useState } from 'react';
import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import {
  AppBar,
  Toolbar,
  IconButton,
  Drawer,
  List,
  ListItem,
  ListItemText,
  useMediaQuery,
  useTheme,
} from '@mui/material';
import {
  Menu as MenuIcon,
  Close as CloseIcon,
  LocalHospital as ClinicIcon,
  CalendarMonth,
  MedicalServices,
} from '@mui/icons-material';

export default function Header() {
  const [mobileOpen, setMobileOpen] = useState(false);
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));

  const menuItems = [
    { text: 'Home', path: '/', icon: <ClinicIcon /> },
    { text: 'Agendamentos', path: '/agendamentos', icon: <CalendarMonth /> },
    { text: 'Médicos', path: '/medicos', icon: <MedicalServices /> },
  ];

  const handleDrawerToggle = () => {
    setMobileOpen(!mobileOpen);
  };

  return (
    <>
      <AppBar
        position="sticky"
        className="bg-linear-to-r from-teal-600 to-cyan-600 shadow-lg"
      >
        <Toolbar className="max-w-7xl w-full mx-auto px-4">
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.5 }}
            className="flex-1"
          >
            <Link
              to="/"
              className="flex items-center gap-2 text-white no-underline"
            >
              <ClinicIcon className="text-3xl" />
              <div className="flex flex-col">
                <span className="text-2xl font-bold tracking-wide">CLINAB</span>
                <span className="text-xs opacity-90 hidden sm:block">
                  Cuidando da sua saúde
                </span>
              </div>
            </Link>
          </motion.div>

          {isMobile ? (
            <IconButton
              color="inherit"
              aria-label="abrir menu"
              edge="end"
              onClick={handleDrawerToggle}
            >
              <MenuIcon />
            </IconButton>
          ) : (
            <motion.nav
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ duration: 0.5, delay: 0.2 }}
              className="flex gap-1"
            >
              {menuItems.map((item, index) => (
                <motion.div
                  key={item.path}
                  initial={{ opacity: 0, y: -10 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.3, delay: 0.1 * index }}
                >
                  <Link
                    to={item.path}
                    className="px-4 py-2 text-white no-underline rounded-lg hover:bg-white/10 transition-all duration-300 flex items-center gap-2"
                  >
                    {item.icon}
                    <span>{item.text}</span>
                  </Link>
                </motion.div>
              ))}
            </motion.nav>
          )}
        </Toolbar>
      </AppBar>

      <Drawer
        anchor="right"
        open={mobileOpen}
        onClose={handleDrawerToggle}
        className="md:hidden"
      >
        <div className="w-64 bg-linear-to-b from-teal-600 to-cyan-600 h-full text-white">
          <div className="flex justify-between items-center p-4 border-b border-white/20">
            <div className="flex items-center gap-2">
              <ClinicIcon />
              <span className="text-xl font-bold">CLINAB</span>
            </div>
            <IconButton onClick={handleDrawerToggle} className="text-white">
              <CloseIcon className="text-white" />
            </IconButton>
          </div>
          <List>
            {menuItems.map(item => (
              <ListItem
                key={item.path}
                component={Link}
                to={item.path}
                onClick={handleDrawerToggle}
                className="text-white hover:bg-white/10 transition-all"
              >
                <div className="flex items-center gap-3 text-white">
                  {item.icon}
                  <ListItemText primary={item.text} />
                </div>
              </ListItem>
            ))}
          </List>
        </div>
      </Drawer>
    </>
  );
}
