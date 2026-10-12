export const formatNumber=n=>new Intl.NumberFormat().format(n);
export const initials=name=>name.split(' ').map(p=>p[0]).slice(0,2).join('').toUpperCase();
