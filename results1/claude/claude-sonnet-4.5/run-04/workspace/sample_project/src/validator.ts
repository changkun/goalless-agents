/**
 * Data validation utilities
 */

interface ValidationRule {
  field: string;
  type: 'string' | 'number' | 'email' | 'url';
  required?: boolean;
  min?: number;
  max?: number;
}

interface ValidationResult {
  valid: boolean;
  errors: string[];
}

export class Validator {
  /**
   * Validate data against rules
   */
  static validate(data: any, rules: ValidationRule[]): ValidationResult {
    const errors: string[] = [];

    for (const rule of rules) {
      const value = data[rule.field];

      // Check required
      if (rule.required && (value === undefined || value === null)) {
        errors.push(`${rule.field} is required`);
        continue;
      }

      // Skip validation if not required and not present
      if (!rule.required && (value === undefined || value === null)) {
        continue;
      }

      // Type validation
      if (rule.type === 'string' && typeof value !== 'string') {
        errors.push(`${rule.field} must be a string`);
      } else if (rule.type === 'number' && typeof value !== 'number') {
        errors.push(`${rule.field} must be a number`);
      } else if (rule.type === 'email') {
        if (!this.isValidEmail(value)) {
          errors.push(`${rule.field} must be a valid email`);
        }
      } else if (rule.type === 'url') {
        if (!this.isValidURL(value)) {
          errors.push(`${rule.field} must be a valid URL`);
        }
      }

      // Length/range validation
      if (rule.min !== undefined) {
        if (typeof value === 'string' && value.length < rule.min) {
          errors.push(`${rule.field} must be at least ${rule.min} characters`);
        } else if (typeof value === 'number' && value < rule.min) {
          errors.push(`${rule.field} must be at least ${rule.min}`);
        }
      }

      if (rule.max !== undefined) {
        if (typeof value === 'string' && value.length > rule.max) {
          errors.push(`${rule.field} must be at most ${rule.max} characters`);
        } else if (typeof value === 'number' && value > rule.max) {
          errors.push(`${rule.field} must be at most ${rule.max}`);
        }
      }
    }

    return {
      valid: errors.length === 0,
      errors,
    };
  }

  static isValidEmail(email: string): boolean {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
  }

  static isValidURL(url: string): boolean {
    try {
      new URL(url);
      return true;
    } catch {
      return false;
    }
  }
}
