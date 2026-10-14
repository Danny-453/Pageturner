const FIELD_LABELS = {
  academic_level_id: 'Academic level',
  confirm_password: 'Confirm password',
  email: 'Email',
  full_name: 'Full name',
  new_password: 'New password',
  password: 'Password',
  student_id: 'Student ID',
  token: 'Reset token',
};

function fieldLabel(location) {
  if (!Array.isArray(location)) return '';
  const field = [...location].reverse().find((part) => !['body', 'query', 'path'].includes(part));
  if (typeof field !== 'string') return '';
  return FIELD_LABELS[field] ?? field.replaceAll('_', ' ').replace(/^./, (letter) => letter.toUpperCase());
}

export function formatValidationError(error) {
  const label = fieldLabel(error.loc);
  const message = error.msg ?? 'Invalid value.';
  if (!label) return message;

  const tooShort = message.match(/should have at least (\d+) characters?\.?$/i);
  if (tooShort) return `${label} must be at least ${tooShort[1]} characters.`;

  const tooLong = message.match(/should have at most (\d+) characters?\.?$/i);
  if (tooLong) return `${label} must be at most ${tooLong[1]} characters.`;

  return `${label}: ${message}`;
}
