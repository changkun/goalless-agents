import { execSync } from 'child_process';
import Anthropic from '@anthropic-ai/sdk';

const client = new Anthropic({
  apiKey: process.env.ANTHROPIC_API_KEY,
});

export async function getRecentCommits(limit = 10) {
  try {
    const output = execSync(
      `git log --oneline -${limit} --format="%h %s (%an)"`,
      { encoding: 'utf-8' }
    );
    return output.trim().split('\n').filter(line => line);
  } catch (error) {
    throw new Error(`Failed to fetch git commits: ${error.message}`);
  }
}

export async function generateStandup(commits) {
  if (!commits.length) {
    throw new Error('No commits provided');
  }

  const commitText = commits.join('\n');
  const prompt = `You are a helpful assistant that summarizes git commits into a concise daily standup summary.

Given the following recent git commits from a developer's work:

${commitText}

Generate a brief, professional standup summary with:
- 3-5 bullet points describing what was accomplished
- Focus on the work items and features, not technical details
- Use clear, simple language
- Be concise (2-3 lines per bullet)

Format as plain bullet points (- prefix).`;

  const message = await client.messages.create({
    model: 'claude-opus-4-6',
    max_tokens: 500,
    messages: [
      {
        role: 'user',
        content: prompt,
      },
    ],
  });

  const content = message.content[0];
  if (content.type !== 'text') {
    throw new Error('Unexpected response type from Claude');
  }

  return content.text;
}

export async function generateStandupFromGit(commitLimit = 10) {
  const commits = await getRecentCommits(commitLimit);
  const summary = await generateStandup(commits);
  return { commits, summary };
}
