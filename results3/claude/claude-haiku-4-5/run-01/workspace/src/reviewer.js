import Anthropic from '@anthropic-ai/sdk';
import path from 'path';

const client = new Anthropic();

export async function reviewCode(content, filePath) {
  const extension = path.extname(filePath);
  const filename = path.basename(filePath);

  const prompt = `You are an expert code reviewer. Review the following ${getLanguageName(extension)} code and provide constructive, detailed feedback.

Focus on:
1. Code quality and readability
2. Potential bugs or logical issues
3. Performance considerations
4. Best practices for the language
5. Security concerns
6. Maintainability

File: ${filename}

\`\`\`${getLanguageId(extension)}
${content}
\`\`\`

Provide a thorough but concise review. Be specific about line numbers or code sections when possible.`;

  const message = await client.messages.create({
    model: 'claude-opus-4-6',
    max_tokens: 1500,
    messages: [
      {
        role: 'user',
        content: prompt,
      },
    ],
  });

  return message.content[0].type === 'text' ? message.content[0].text : '';
}

function getLanguageName(ext) {
  const languages = {
    '.js': 'JavaScript',
    '.ts': 'TypeScript',
    '.py': 'Python',
    '.java': 'Java',
    '.cpp': 'C++',
    '.c': 'C',
    '.go': 'Go',
    '.rb': 'Ruby',
    '.php': 'PHP',
    '.rs': 'Rust',
    '.swift': 'Swift',
    '.kt': 'Kotlin',
    '.cs': 'C#',
  };
  return languages[ext] || 'source';
}

function getLanguageId(ext) {
  const ids = {
    '.js': 'javascript',
    '.ts': 'typescript',
    '.py': 'python',
    '.java': 'java',
    '.cpp': 'cpp',
    '.c': 'c',
    '.go': 'go',
    '.rb': 'ruby',
    '.php': 'php',
    '.rs': 'rust',
    '.swift': 'swift',
    '.kt': 'kotlin',
    '.cs': 'csharp',
  };
  return ids[ext] || 'text';
}
