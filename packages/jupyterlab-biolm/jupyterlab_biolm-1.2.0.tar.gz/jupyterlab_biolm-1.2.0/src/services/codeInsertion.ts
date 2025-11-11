/**
 * Service for inserting code snippets into notebook cells
 */
import { INotebookTracker } from '@jupyterlab/notebook';
import { showErrorMessage } from '@jupyterlab/apputils';

/**
 * Generate a code snippet for a model and action
 * Based on BioLM SDK format: https://docs.biolm.ai/latest/python-client/usage.html
 */
export function generateSnippet(
  modelId: string, 
  action: string, 
  codeExample?: string
): string {
  // If we have a code example from the API, use it as-is
  if (codeExample) {
    return codeExample;
  }
  
  // Fallback: minimal code example with comment
  // Determine the type based on action
  let itemType = "sequence";
  let exampleItem = '"YOUR_SEQUENCE_HERE"';
  
  if (action === "generate") {
    itemType = "context";
    exampleItem = '"YOUR_CONTEXT_HERE"';
  }
  
  return `# Complete example not available
result = biolm(entity="${modelId}", action="${action}", type="${itemType}", items=${exampleItem})

print(result)`;
}

/**
 * Set BIOLMAI_TOKEN environment variable in the notebook kernel
 */
export async function setTokenInKernel(
  notebookTracker: INotebookTracker,
  apiKey: string
): Promise<boolean> {
  const current = notebookTracker.currentWidget;
  
  if (!current) {
    return false;
  }

  const sessionContext = current.sessionContext;
  
  if (!sessionContext || !sessionContext.session?.kernel) {
    return false;
  }

  try {
    const kernel = sessionContext.session.kernel;
    // Escape single quotes in the API key
    const escapedKey = apiKey.replace(/'/g, "\\'").replace(/\\/g, "\\\\");
    const code = `import os\nos.environ['BIOLMAI_TOKEN'] = '${escapedKey}'`;
    
    // Execute code silently in the kernel (silent=true means no output)
    const future = kernel.requestExecute({ code, silent: true });
    
    // Wait for execution to complete
    await future.done;
    return true;
  } catch (error) {
    console.error('Failed to set BIOLMAI_TOKEN in kernel:', error);
    return false;
  }
}

/**
 * Insert code into the active notebook cell
 */
export async function insertCode(
  notebookTracker: INotebookTracker,
  code: string,
  append: boolean = true
): Promise<boolean> {
  const current = notebookTracker.currentWidget;
  
  if (!current) {
    await showErrorMessage(
      'No Active Notebook',
      'Please open a notebook before inserting code.'
    );
    return false;
  }

  const notebook = current.content;
  const activeCell = notebook.activeCell;

  if (!activeCell) {
    await showErrorMessage(
      'No Active Cell',
      'Please select a cell in the notebook.'
    );
    return false;
  }

  const cellModel = activeCell.model;
  const sharedModel = cellModel.sharedModel;
  const currentText = sharedModel.getSource();

  if (append && currentText.trim()) {
    // Append with newline if cell has content
    sharedModel.setSource(currentText + '\n' + code);
  } else {
    // Replace or insert into empty cell
    sharedModel.setSource(code);
  }

  return true;
}
