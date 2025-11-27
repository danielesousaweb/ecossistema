/**
 * Utilitários de formatação para o Tech Mesh Sync
 */

/**
 * Capitaliza a primeira letra de cada frase
 * @param {string} str - String para capitalizar
 * @returns {string} String capitalizada
 */
export const capitalize = (str) => {
  if (!str) return '';
  return str.charAt(0).toUpperCase() + str.slice(1);
};

/**
 * Capitaliza primeira letra de cada palavra
 * @param {string} str - String para capitalizar
 * @returns {string} String com cada palavra capitalizada
 */
export const capitalizeWords = (str) => {
  if (!str) return '';
  return str
    .split(' ')
    .map(word => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase())
    .join(' ');
};

/**
 * Converte valores booleanos para Sim/Não
 * @param {any} value - Valor para converter
 * @returns {string} "Sim", "Não" ou valor original
 */
export const formatBoolean = (value) => {
  if (value === true || value === 'true' || value === 'True' || value === '1') {
    return 'Sim';
  }
  if (value === false || value === 'false' || value === 'False' || value === '0') {
    return 'Não';
  }
  return value;
};

/**
 * Formata valor para exibição (aplica todas as regras)
 * @param {any} value - Valor para formatar
 * @returns {string} Valor formatado
 */
export const formatValue = (value) => {
  if (value === null || value === undefined) return '-';
  
  // Converter booleanos
  const booleanValue = formatBoolean(value);
  if (booleanValue === 'Sim' || booleanValue === 'Não') {
    return booleanValue;
  }
  
  // Se for string, capitalizar
  if (typeof value === 'string') {
    // Substituir underscores por espaços
    let formatted = value.replace(/_/g, ' ');
    // Capitalizar
    formatted = capitalize(formatted);
    return formatted;
  }
  
  return String(value);
};

/**
 * Formata nome de campo (remove underscores, capitaliza)
 * @param {string} fieldName - Nome do campo
 * @returns {string} Nome formatado
 */
export const formatFieldName = (fieldName) => {
  if (!fieldName) return '';
  return capitalizeWords(fieldName.replace(/_/g, ' '));
};
