import Anthropic from '@anthropic-ai/sdk';

const client = new Anthropic();

/**
 * Parse review text into structured data for JSON output
 * Uses Claude to extract key information from the review
 */
async function parseReviewForJSON(reviewText) {
  try {
    const parsePrompt = `Extract structured data from this code review. Return JSON with these fields:
- issues: array of {severity: "critical"|"warning"|"suggestion", title: string, description: string}
- summary: brief overall assessment (1-2 sentences)
- total_issues: number

Review text:
${reviewText}

Respond with ONLY valid JSON, no other text.`;

    const message = await client.messages.create({
      model: 'claude-opus-4-6',
      max_tokens: 1000,
      messages: [{ role: 'user', content: parsePrompt }],
    });

    const responseText =
      message.content[0].type === 'text' ? message.content[0].text : '{}';

    try {
      return JSON.parse(responseText);
    } catch {
      // If parsing fails, return the raw review as fallback
      return {
        issues: [
          {
            severity: 'info',
            title: 'Code Review',
            description: reviewText,
          },
        ],
        summary: 'Review completed',
        total_issues: 1,
      };
    }
  } catch {
    // On error, return minimal structure
    return {
      issues: [
        { severity: 'info', title: 'Review', description: reviewText }
      ],
      summary: 'Review completed',
      total_issues: 1,
    };
  }
}

/**
 * Format review output as JSON
 */
export async function formatAsJSON(reviewText, filePath, diffMode = false) {
  const parsedData = await parseReviewForJSON(reviewText);

  return {
    type: diffMode ? 'diff_review' : 'file_review',
    file: filePath || 'git diff',
    timestamp: new Date().toISOString(),
    review: reviewText,
    structured: parsedData,
  };
}

/**
 * Format review output as plain text
 */
export function formatAsText(reviewText, title = 'CODE REVIEW') {
  return (
    '\n' + '='.repeat(60) + '\n' + title + '\n' + '='.repeat(60) + '\n\n' +
    reviewText
  );
}
