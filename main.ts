import { copyFileSync, mkdirSync } from 'node:fs';
import { dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const source = resolve(dirname(fileURLToPath(import.meta.url)), 'entry.png');
const directory = resolve(process.env.MAKEFUN_OUTPUT_DIR || '.');
const destination = resolve(directory, 'entry.png');
mkdirSync(directory, { recursive: true });
if (source !== destination) copyFileSync(source, destination);
console.log('Wrote entry.png');
