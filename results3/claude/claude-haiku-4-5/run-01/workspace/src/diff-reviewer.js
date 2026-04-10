import Anthropic from '@anthropic-ai/sdk';
import { execSync } from 'child_process';

const client = new Anthropic();

export async function reviewGitDiff() {
  try {
    const diff = execSync('git diff HEAD', { encoding: 'utf-8' });

    if (!diff.trim()) {
      console.log('No staged changes to review.');
      return;
    }

    const prompt = `You are an expert code reviewer. Review the following git diff and provide constructive feedback on the changes.

Focus on:
1. Correctness of the changes
2. Impact on performance
3. Code quality and readability
4. Potential bugs introduced
5. Security implications
6. Adherence to best practices

\`\`\`diff
${diff}
\`\`\`

Provide a focused review of only the changed lines. Be concise but thorough.`;

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
  } catch (error) {
    if (error.message.includes('fatal: not a git repository')) {
      throw new Error(
        'Not a git repository. Use --file to review a specific file instead.'
      );
    }
    throw error;
  }
}
