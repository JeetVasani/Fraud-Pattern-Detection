import { NextRequest, NextResponse } from 'next/server';
import { exec } from 'child_process';
import { promisify } from 'util';
import fs from 'fs';
import path from 'path';

const execAsync = promisify(exec);

export async function POST(request: NextRequest) {
  try {
    const formData = await request.formData();
    const file = formData.get('file') as File;

    if (!file) {
      return NextResponse.json({ error: 'No file provided' }, { status: 400 });
    }

    // Save the uploaded file temporarily
    const tempDir = path.join(process.cwd(), 'temp');
    if (!fs.existsSync(tempDir)) {
      fs.mkdirSync(tempDir);
    }

    const tempFilePath = path.join(tempDir, `upload_${Date.now()}.csv`);
    const fileBuffer = await file.arrayBuffer();
    fs.writeFileSync(tempFilePath, Buffer.from(fileBuffer));

    // Run the Python script
    const pythonScript = path.join(process.cwd(), 'app', 'backend', 'fraud_detection.py');
    const { stdout, stderr } = await execAsync(`python "${pythonScript}" "${tempFilePath}"`);

    // Clean up the temporary file
    fs.unlinkSync(tempFilePath);

    if (stderr) {
      console.error('Python script error:', stderr);
      return NextResponse.json({ error: 'Error processing file' }, { status: 500 });
    }

    // Parse the JSON output from Python
    const result = JSON.parse(stdout.trim());

    return NextResponse.json(result);
  } catch (error) {
    console.error('Error:', error);
    return NextResponse.json({ error: 'Internal server error' }, { status: 500 });
  }
}
