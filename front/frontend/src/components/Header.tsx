import { useState } from 'react';
import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import {
  Avatar,
  AppBar,
  Divider,
  Toolbar,
  IconButton,
  Drawer,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Menu,
  MenuItem,
  useMediaQuery,
  useTheme,
} from '@mui/material';
import {
  Menu as MenuIcon,
  Close as CloseIcon,
  LocalHospital as ClinicIcon,
  CalendarMonth,
  ExpandMore,
  Logout,
  MedicalServices,
} from '@mui/icons-material';

function parseJwtPayload(token: string): Record<string, unknown> | null {
  try {
    const payloadBase64Url = token.split('.')[1];
    if (!payloadBase64Url) return null;

    const payloadBase64 = payloadBase64Url
      .replace(/-/g, '+')
      .replace(/_/g, '/');
    const payload = window.atob(payloadBase64);
    return JSON.parse(payload) as Record<string, unknown>;
  } catch {
    return null;
  }
}

function getStoredUsername(): string {
  const displayName = localStorage.getItem('authDisplayName')?.trim();
  if (displayName) return displayName;

  const stored = localStorage.getItem('username')?.trim();
  if (stored) return stored;

  const token = localStorage.getItem('token');
  if (!token) return 'Usuario';

  const payload = parseJwtPayload(token);
  const tokenUsername =
    (typeof payload?.username === 'string' && payload.username) ||
    (typeof payload?.name === 'string' && payload.name) ||
    (typeof payload?.given_name === 'string' && payload.given_name) ||
    (typeof payload?.email === 'string' && payload.email.split('@')[0]) ||
    null;

  if (tokenUsername) {
    localStorage.setItem('username', tokenUsername);
    return tokenUsername;
  }

  return 'Usuario';
}

export default function Header() {
  const [mobileOpen, setMobileOpen] = useState(false);
  const [accountAnchorEl, setAccountAnchorEl] = useState<null | HTMLElement>(
    null,
  );
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));
  const isAccountMenuOpen = Boolean(accountAnchorEl);

  const isLoggedIn = Boolean(localStorage.getItem('token'));
  const username = getStoredUsername();
  const userInitial = username.charAt(0).toUpperCase();

  const menuItems = [
    { text: 'Home', path: '/', icon: <ClinicIcon /> },
    { text: 'Agendamentos', path: '/agendamentos', icon: <CalendarMonth /> },
    { text: 'Médicos', path: '/medicos', icon: <MedicalServices /> },
  ];

  const handleDrawerToggle = () => {
    setMobileOpen(!mobileOpen);
  };

  const handleOpenAccountMenu = (event: React.MouseEvent<HTMLElement>) => {
    setAccountAnchorEl(event.currentTarget);
  };

  const handleCloseAccountMenu = () => {
    setAccountAnchorEl(null);
  };

  const handleLogout = () => {
    handleCloseAccountMenu();
    localStorage.removeItem('token');
    localStorage.removeItem('refreshToken');
    localStorage.removeItem('username');
    localStorage.removeItem('authDisplayName');
    window.location.href = '/auth?mode=register';
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

              {isLoggedIn && (
                <motion.div
                  initial={{ opacity: 0, y: -10 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.3, delay: 0.1 * menuItems.length }}
                  className="ml-2"
                >
                  <button
                    type="button"
                    onClick={handleOpenAccountMenu}
                    className="group flex items-center gap-2 rounded-full border border-white/30 bg-white/12 px-2 py-1 text-white shadow-lg shadow-cyan-900/15 backdrop-blur-sm transition-all duration-300 hover:bg-white/22 hover:border-white/45"
                    aria-label="abrir menu da conta"
                  >
                    <Avatar
                      sx={{
                        width: 30,
                        height: 30,
                        fontSize: 14,
                        fontWeight: 700,
                      }}
                      className="bg-white/25 text-white"
                    >
                      {userInitial}
                    </Avatar>
                    <span className="text-sm font-medium pr-0.5">
                      {username}
                    </span>
                    <ExpandMore className="text-white/90 group-hover:translate-y-px transition-transform" />
                  </button>

                  <Menu
                    anchorEl={accountAnchorEl}
                    open={isAccountMenuOpen}
                    onClose={handleCloseAccountMenu}
                    transformOrigin={{ horizontal: 'right', vertical: 'top' }}
                    anchorOrigin={{ horizontal: 'right', vertical: 'bottom' }}
                    PaperProps={{
                      className:
                        'mt-2 min-w-[180px] rounded-xl border border-slate-200 shadow-xl',
                    }}
                  >
                    <MenuItem onClick={handleLogout} className="py-2.5">
                      <ListItemIcon>
                        <Logout fontSize="small" className="text-rose-500" />
                      </ListItemIcon>
                      <ListItemText primary="Sair" className="text-slate-700" />
                    </MenuItem>
                  </Menu>
                </motion.div>
              )}
            </motion.nav>
          )}
        </Toolbar>
      </AppBar>

      <Drawer anchor="right" open={mobileOpen} onClose={handleDrawerToggle}>
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

          {isLoggedIn && (
            <div className="mx-4 mt-4 mb-2 rounded-xl border border-white/25 bg-white/10 p-3 backdrop-blur-sm">
              <div className="flex items-center gap-3">
                <Avatar
                  sx={{ width: 34, height: 34, fontSize: 15, fontWeight: 700 }}
                  className="bg-white/25 text-white"
                >
                  {userInitial}
                </Avatar>
                <div className="min-w-0">
                  <p className="text-xs text-white/80">Conectado como</p>
                  <p className="text-sm font-semibold truncate">{username}</p>
                </div>
              </div>
            </div>
          )}

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

            {isLoggedIn && (
              <>
                <Divider className="border-white/20" />
                <ListItem
                  onClick={() => {
                    handleDrawerToggle();
                    handleLogout();
                  }}
                  className="text-white hover:bg-white/10 transition-all cursor-pointer"
                >
                  <div className="flex items-center gap-3 text-white">
                    <Logout />
                    <ListItemText primary="Sair" />
                  </div>
                </ListItem>
              </>
            )}
          </List>
        </div>
      </Drawer>
    </>
  );
}
