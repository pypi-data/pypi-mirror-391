# CommitAid - AI Commit Message Generator

You are helping generate a git commit message based on the current staged changes.

## Task

1. Run `git status` to see the current state of the repository
2. Run `git diff --cached` to see the staged changes
3. Analyze the changes and generate a clear, descriptive commit message

## Commit Message Guidelines

Follow the commit guidelines from the `COMMITAID_SPEC` environment variable.

## Output Format

Do not include any additional commentary, explanations, or formatting - just the raw commit message that can be used directly with `git commit`.
