import { AppStateService } from '../AppState';
import { ChatMessages } from '../Chat/ChatMessages';
import { IToolCall, IChatMessage } from '../types';
import { ToolService } from '../Services/ToolService';
import testHistory from './test_sp.json';
import { NotebookTools } from '../Notebook/NotebookTools';
import { NotebookActions } from '@jupyterlab/notebook';
import { DemoControlPanel } from './DemoControlPanel';
import { IChatThread } from '../Chat/ChatHistoryManager';
import { v4 as uuidv4 } from 'uuid';
import {
  handleEditPlan,
  skipToResult,
  executeAllCells,
  isEditPlanTool,
  isRunCellTool,
  processDemoMessages
} from './demo_cell_actions';

/**
 * Demo message system that directly interacts with ChatMessages
 * to add and stream messages without using the API
 *
 * CELL STREAMING CONFIGURATION:
 * To adjust the speed of cell content generation, modify CELL_STREAMING_CONFIG below:
 * - baseDelay: Higher = slower generation (in milliseconds)
 * - minChunkSize/maxChunkSize: Control characters per chunk
 * - variationFactor: Controls randomness (0-1, higher = more variation)
 */

// Global flag to control streaming vs instant mode
let isSkipToResultMode = false;
let demoControlPanel: DemoControlPanel | null = null;
let isDemoAborted = false; // Flag to abort ongoing demo

// Track overlay elements for cleanup
const overlayElements: HTMLElement[] = [];

/**
 * Create a reusable grey overlay with tooltip
 */
function createOverlay(zIndex: number = 9999): HTMLElement {
  const overlay = document.createElement('div');
  overlay.className = 'sage-demo-overlay';
  overlay.style.cssText = `
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background-color: rgba(128, 128, 128, 0.3);
    z-index: ${zIndex};
    cursor: not-allowed;
    pointer-events: auto;
  `;

  // Add tooltip
  overlay.title = 'Disabled on replay';

  overlayElements.push(overlay);
  return overlay;
}

/**
 * Replace send button SVG with spinner
 */
function replaceSendButtonWithSpinner(): void {
  const sendButton = document.querySelector(
    '.sage-ai-send-button'
  ) as HTMLElement;
  if (sendButton) {
    // Store original content for restoration
    sendButton.dataset.originalContent = sendButton.innerHTML;

    // Create spinner SVG
    const spinner = document.createElement('div');
    spinner.className = 'sage-demo-spinner';
    spinner.innerHTML = `
      <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#7A7A7A" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <circle cx="12" cy="12" r="10" opacity="0.25"/>
        <path d="M12 2a10 10 0 0 1 10 10" opacity="0.75">
          <animateTransform attributeName="transform" type="rotate" from="0 12 12" to="360 12 12" dur="1s" repeatCount="indefinite"/>
        </path>
      </svg>
    `;

    sendButton.innerHTML = '';
    sendButton.appendChild(spinner);
  }
}

/**
 * Restore send button original SVG
 */
function restoreSendButton(): void {
  const sendButton = document.querySelector(
    '.sage-ai-send-button'
  ) as HTMLElement;
  if (sendButton && sendButton.dataset.originalContent) {
    sendButton.innerHTML = sendButton.dataset.originalContent;
    delete sendButton.dataset.originalContent;
  }
}

/**
 * Hide and disable all UI components during demo mode
 */
export function hide_all_components(): void {
  console.log('[Demo] Hiding and disabling UI components');

  // 1. Add overlay to sage-ai-chatbox-wrapper
  const chatboxWrapper = document.querySelector(
    '.sage-ai-chatbox-wrapper'
  ) as HTMLElement;
  if (chatboxWrapper) {
    chatboxWrapper.style.position = 'relative';
    const overlay = createOverlay(9999);
    chatboxWrapper.appendChild(overlay);
  }

  // 2. Replace send button SVG with spinner
  replaceSendButtonWithSpinner();

  // 3. Add overlay to sage-ai-toolbar
  const toolbar = document.querySelector('.sage-ai-toolbar') as HTMLElement;
  if (toolbar) {
    toolbar.style.position = 'relative';
    const overlay = createOverlay(9999);
    toolbar.appendChild(overlay);
  }

  // 4. Add overlay to right sidebar (lm-Widget lm-TabBar jp-SideBar jp-mod-right lm-BoxPanel-child)
  const rightSidebar = document.querySelector(
    '.lm-Widget.lm-TabBar.jp-SideBar.jp-mod-right.lm-BoxPanel-child'
  ) as HTMLElement;
  if (rightSidebar) {
    rightSidebar.style.position = 'relative';
    const overlay = createOverlay(9999);
    rightSidebar.appendChild(overlay);
  }

  // 5. Add overlay to left sidebar (lm-Widget lm-TabBar jp-SideBar jp-mod-left lm-BoxPanel-child)
  const leftSidebar = document.querySelector(
    '.lm-Widget.lm-TabBar.jp-SideBar.jp-mod-left.lm-BoxPanel-child'
  ) as HTMLElement;
  if (leftSidebar) {
    leftSidebar.style.position = 'relative';
    const overlay = createOverlay(9999);
    leftSidebar.appendChild(overlay);
  }

  // 6. Add overlay to notebook toolbar (lm-Widget jp-Toolbar jp-NotebookPanel-toolbar)
  const notebookToolbar = document.querySelector(
    '.lm-Widget.jp-Toolbar.jp-NotebookPanel-toolbar'
  ) as HTMLElement;
  if (notebookToolbar) {
    notebookToolbar.style.position = 'relative';
    const overlay = createOverlay(9999);
    notebookToolbar.appendChild(overlay);
  }

  // 7. Add overlay to top panel (id=jp-top-panel)
  const topPanel = document.getElementById('jp-top-panel') as HTMLElement;
  if (topPanel) {
    topPanel.style.position = 'relative';
    const overlay = createOverlay(9999);
    topPanel.appendChild(overlay);
  }
}

/**
 * Show and re-enable all UI components after demo mode
 */
export function show_all_components(): void {
  console.log('[Demo] Showing and re-enabling UI components');

  // Remove all overlays
  overlayElements.forEach(overlay => {
    overlay.remove();
  });
  overlayElements.length = 0; // Clear the array

  // Restore send button
  restoreSendButton();
}

export interface DemoTextBlock {
  type: 'text';
  text: string;
}

export interface DemoToolUseBlock {
  type: 'tool_use';
  id: string;
  name: string;
  input: any;
  result?: string; // Optional tool result content
}

export type DemoContentBlock = DemoTextBlock | DemoToolUseBlock;

export interface DemoMessage {
  role: 'user' | 'assistant';
  content: string | DemoContentBlock[];
}

/**
 * Send a demo message directly to the chat interface
 * This bypasses the API and directly manipulates the ChatMessages component
 */
export async function sendDemoMessage(
  chatMessages: ChatMessages,
  message: DemoMessage,
  streamingDelay: number = 20,
  nextMessage?: DemoMessage
): Promise<void> {
  if (message.role === 'user') {
    // Add user message directly
    await addDemoUserMessage(chatMessages, message.content as string);
  } else if (message.role === 'assistant') {
    // Stream assistant message
    await streamDemoAssistantMessage(
      chatMessages,
      message.content,
      streamingDelay,
      nextMessage
    );
  }
}

/**
 * Add a user message to the chat (demo mode)
 */
async function addDemoUserMessage(
  chatMessages: ChatMessages,
  content: string
): Promise<void> {
  // Add the user message directly to the UI without saving to history
  chatMessages.addUserMessage(content, false, true); // is_demo = true

  // Small delay to simulate user input
  await delay(300);
}

/**
 * Stream an assistant message to the chat (demo mode)
 */
async function streamDemoAssistantMessage(
  chatMessages: ChatMessages,
  content: string | DemoContentBlock[],
  streamingDelay: number,
  nextMessage?: DemoMessage
): Promise<void> {
  // Handle text content
  if (typeof content === 'string') {
    await streamDemoText(chatMessages, content, streamingDelay);
    return;
  }

  // Handle content blocks (text and tool calls)
  if (Array.isArray(content)) {
    for (const block of content) {
      if (block.type === 'text') {
        await streamDemoText(chatMessages, block.text, streamingDelay);
      } else if (block.type === 'tool_use') {
        // The tool result is now attached to the tool_use block
        await streamDemoToolUse(chatMessages, block, block.result);
      }
    }
  }
}

/**
 * Stream text content character by character
 * In skip mode, this will instantly show the full text
 */
async function streamDemoText(
  chatMessages: ChatMessages,
  text: string,
  streamingDelay: number
): Promise<void> {
  // Check if demo was aborted
  if (isDemoAborted) {
    console.log('[Demo] Aborting text streaming - demo was stopped');
    return;
  }

  // Create streaming message container
  const messageElement = chatMessages.addStreamingAIMessage();

  if (isSkipToResultMode) {
    // In skip mode, add all text at once
    await chatMessages.updateStreamingMessage(messageElement, text);
    await chatMessages.finalizeStreamingMessage(messageElement, true);
    return;
  }

  // Normal streaming mode: Stream the text in chunks
  const chunkSize = 3; // Characters per chunk
  for (let i = 0; i < text.length; i += chunkSize) {
    // Check if demo was aborted
    if (isDemoAborted) {
      console.log('[Demo] Aborting text streaming mid-stream');
      return;
    }

    const chunk = text.slice(i, i + chunkSize);
    await chatMessages.updateStreamingMessage(messageElement, chunk);
    await delay(streamingDelay);
  }

  // Finalize the streaming message (is_demo = true)
  await chatMessages.finalizeStreamingMessage(messageElement, true);
}

/**
 * Configuration for cell streaming effect
 */
export const CELL_STREAMING_CONFIG = {
  // Base delay between chunks in milliseconds (adjust this to speed up/slow down)
  baseDelay: 10,
  // Minimum chunk size in characters
  minChunkSize: 4,
  // Maximum chunk size in characters
  maxChunkSize: 10,
  // Variation factor (0-1, higher = more variation)
  variationFactor: 0.3
};

/**
 * Generate random chunk size with natural variation
 */
function getRandomChunkSize(): number {
  const { minChunkSize, maxChunkSize, variationFactor } = CELL_STREAMING_CONFIG;
  const range = maxChunkSize - minChunkSize;
  const baseSize = minChunkSize + Math.floor(Math.random() * range);
  const variation = Math.floor(
    (Math.random() - 0.5) * 2 * variationFactor * range
  );
  return Math.max(minChunkSize, Math.min(maxChunkSize, baseSize + variation));
}

/**
 * Stream cell content with LLM-like generation effect
 * In skip mode, this will instantly set the full content
 */
async function streamCellContent(
  toolService: any,
  cellId: string,
  fullContent: string,
  summary: string,
  notebookPath: string,
  isAddCell: boolean = false
): Promise<void> {
  // Check if demo was aborted
  if (isDemoAborted) {
    console.log('[Demo] Aborting cell streaming - demo was stopped');
    return;
  }

  // In skip mode, just set the full content immediately
  if (isSkipToResultMode) {
    if (isAddCell) {
      toolService.notebookTools?.edit_cell({
        cell_id: cellId,
        new_source: fullContent,
        summary: summary,
        is_tracking_id: true,
        notebook_path: notebookPath
      });
    } else {
      toolService.notebookTools?.edit_cell({
        cell_id: cellId,
        new_source: fullContent,
        summary: summary,
        is_tracking_id: cellId.startsWith('cell_'),
        notebook_path: notebookPath
      });
    }
    return;
  }

  // Normal streaming mode
  let currentContent = '';
  let position = 0;

  while (position < fullContent.length) {
    // Check if demo was aborted
    if (isDemoAborted) {
      console.log('[Demo] Aborting cell streaming mid-stream');
      return;
    }

    // Get random chunk size for natural variation
    const chunkSize = getRandomChunkSize();
    const chunk = fullContent.slice(position, position + chunkSize);
    currentContent += chunk;
    position += chunkSize;

    // Update the cell with accumulated content
    if (isAddCell) {
      // For add_cell, we need to use edit_cell to update existing cell
      toolService.notebookTools?.edit_cell({
        cell_id: cellId,
        new_source: currentContent,
        summary: summary,
        is_tracking_id: true,
        notebook_path: notebookPath
      });
    } else {
      // For edit_cell, just update normally
      toolService.notebookTools?.edit_cell({
        cell_id: cellId,
        new_source: currentContent,
        summary: summary,
        is_tracking_id: cellId.startsWith('cell_'),
        notebook_path: notebookPath
      });
    }

    // Wait before next chunk with slight random variation
    const delayVariation =
      (Math.random() - 0.5) * CELL_STREAMING_CONFIG.baseDelay * 0.2;
    await delay(CELL_STREAMING_CONFIG.baseDelay + delayVariation);
  }
}

/**
 * Stream a tool use (show tool call and execute it using ToolService)
 */
async function streamDemoToolUse(
  chatMessages: ChatMessages,
  toolUse: DemoToolUseBlock,
  toolResultContent?: string
): Promise<void> {
  // Check if demo was aborted
  if (isDemoAborted) {
    console.log('[Demo] Aborting tool use - demo was stopped');
    return;
  }

  // Create the tool call
  const toolCall: IToolCall = {
    id: toolUse.id,
    name: toolUse.name,
    input: toolUse.input
  };

  console.log(
    '[Demo] Streaming tool use:',
    toolUse.name,
    toolUse.id,
    toolUse,
    toolResultContent
  );

  // Check if this is an edit_plan tool - handle it specially
  if (isEditPlanTool(toolUse.name) && toolResultContent) {
    // Add streaming tool call container
    const toolCallContainer = chatMessages.addStreamingToolCall();

    // Small delay to simulate thinking
    await delay(300);

    // Check abort again
    if (isDemoAborted) return;

    // Update the streaming tool call
    chatMessages.updateStreamingToolCall(toolCallContainer, toolCall);

    // Wait a bit to simulate tool execution starting
    await delay(500);

    // Check abort again
    if (isDemoAborted) return;

    // Finalize the tool call (is_demo = true)
    chatMessages.finalizeStreamingToolCall(toolCallContainer, true);

    // Execute the optimized edit_plan handler
    await delay(200);

    // Check abort again
    if (isDemoAborted) return;

    try {
      await handleEditPlan(toolUse, toolResultContent, chatMessages);

      // Add tool result to UI
      chatMessages.addToolResult(
        toolUse.name,
        toolUse.id,
        toolResultContent,
        {
          assistant: {
            content: [toolUse]
          }
        },
        true
      ); // is_demo = true
    } catch (error) {
      console.error(`Error executing edit_plan:`, error);
      const errorContent = `Error: ${error instanceof Error ? error.message : String(error)}`;
      chatMessages.addToolResult(
        toolUse.name,
        toolUse.id,
        errorContent,
        {
          assistant: {
            content: [toolUse]
          }
        },
        true
      ); // is_demo = true
    }
    return;
  }

  // Add streaming tool call container
  const toolCallContainer = chatMessages.addStreamingToolCall();

  // Small delay to simulate thinking
  await delay(300);

  // Check abort again
  if (isDemoAborted) return;

  // Update the streaming tool call
  chatMessages.updateStreamingToolCall(toolCallContainer, toolCall);

  // Wait a bit to simulate tool execution starting
  await delay(500);

  // Check abort again
  if (isDemoAborted) return;

  // Finalize the tool call (is_demo = true)
  chatMessages.finalizeStreamingToolCall(toolCallContainer, true);

  // Check if this is an add_cell or edit_cell operation
  const isAddCell = toolUse.name === 'notebook-add_cell';
  const isEditCell = toolUse.name === 'notebook-edit_cell';
  const isRunCell = toolUse.name === 'notebook-run_cell';

  // In skip mode, skip run_cell operations (they'll be executed all at once at the end)
  if (isRunCell && isSkipToResultMode) {
    console.log('[Demo] Skip mode: Skipping run_cell, will execute all at end');
    chatMessages.addToolResult(
      toolUse.name,
      toolUse.id,
      'Cell execution skipped - will run all cells at end',
      {
        assistant: {
          content: [toolUse]
        }
      },
      true
    );
    return;
  }

  // Execute the tool using ToolService
  await delay(200);

  // Check abort again
  if (isDemoAborted) return;

  let resultContent: string;

  try {
    const toolService = AppStateService.getToolService();

    // Handle cell operations with streaming effect
    if (isAddCell && toolUse.input.source) {
      // First, create the cell with empty content
      const cellId = toolService.notebookTools?.add_cell({
        cell_type: toolUse.input.cell_type || 'code',
        summary: toolUse.input.summary || 'Creating cell...',
        source: '', // Start with empty content
        notebook_path: toolUse.input.notebook_path,
        position: toolUse.input.position
      });

      if (cellId) {
        // Now stream the content into the cell
        await streamCellContent(
          toolService,
          cellId,
          toolUse.input.source,
          toolUse.input.summary || 'Creating cell...',
          toolUse.input.notebook_path,
          true // isAddCell
        );

        // Check abort before running markdown cell
        if (isDemoAborted) return;

        // If it's a markdown cell, run it to render the content
        const isMarkdown = toolUse.input.cell_type === 'markdown';
        if (isMarkdown && toolService.notebookTools) {
          await delay(100); // Small delay before running
          await toolService.notebookTools.run_cell({
            cell_id: cellId,
            notebook_path: toolUse.input.notebook_path
          });
        }

        resultContent = cellId;
      } else {
        throw new Error('Failed to create cell');
      }
    } else if (isEditCell && toolUse.input.new_source) {
      // For edit_cell, stream the new content
      await streamCellContent(
        toolService,
        toolUse.input.cell_id,
        toolUse.input.new_source,
        toolUse.input.summary || 'Editing cell...',
        toolUse.input.notebook_path,
        false // not isAddCell
      );

      // Check abort before running markdown cell
      if (isDemoAborted) return;

      // If it's a markdown cell, run it to render the content
      const isMarkdown = toolUse.input.cell_type === 'markdown';
      if (isMarkdown && toolService.notebookTools) {
        await delay(100); // Small delay before running
        await toolService.notebookTools.run_cell({
          cell_id: toolUse.input.cell_id,
          notebook_path: toolUse.input.notebook_path
        });
      }

      resultContent = 'true';
    } else {
      // Execute other tools normally
      const result = await toolService.executeTool(toolCall);

      // Extract the content from the tool result
      if (result && result.content) {
        if (typeof result.content === 'string') {
          resultContent = result.content;
        } else if (Array.isArray(result.content)) {
          // Handle array of content blocks
          resultContent = result.content
            .map((item: any) => item.text || JSON.stringify(item))
            .join('\n');
        } else {
          resultContent = JSON.stringify(result.content);
        }
      } else {
        resultContent = JSON.stringify(result);
      }
    }
  } catch (error) {
    console.error(`Error executing tool ${toolUse.name}:`, error);
    resultContent = `Error: ${error instanceof Error ? error.message : String(error)}`;
  }

  // Check abort before adding tool result
  if (isDemoAborted) return;

  chatMessages.addToolResult(
    toolUse.name,
    toolUse.id,
    resultContent,
    {
      assistant: {
        content: [toolUse]
      }
    },
    true
  ); // is_demo = true
}

/**
 * Run a complete demo sequence
 * @param messages Demo messages to run
 * @param streamingDelay Delay between streaming chunks (ignored in skip mode)
 * @param showControlPanel Whether to show the control panel (default: true)
 */
export async function runDemoSequence(
  messages: DemoMessage[],
  streamingDelay: number = 20,
  showControlPanel: boolean = true
): Promise<void> {
  const chatContainer = AppStateService.getChatContainerSafe();
  if (!chatContainer || !chatContainer.chatWidget) {
    console.error('[Demo] Chat container not available');
    throw new Error('Chat container not available');
  }

  const chatMessages = chatContainer.chatWidget.messageComponent;
  const chatHistoryManager = chatContainer.chatWidget.chatHistoryManager;
  chatMessages.scrollToBottom();

  // Reset skip mode and abort flag
  isSkipToResultMode = false;
  isDemoAborted = false;

  // Store the messages for later use
  let demoMessages = messages;
  let demoStarted = false;
  let newThread: any = null;

  const startDemo = async (skipMode: boolean = false) => {
    if (demoStarted) return;
    demoStarted = true;

    isSkipToResultMode = skipMode;

    console.log(
      `[Demo] Starting demo in ${skipMode ? 'SKIP' : 'INTERACTIVE'} mode`
    );

    // Create a new empty thread to clear chat history
    newThread = chatHistoryManager.createNewThread('Temporary Demo Thread');
    if (!newThread) {
      console.error('[Demo] Failed to create new thread');
      throw new Error('Failed to create new thread');
    }

    // Load the empty thread to clear all messages properly
    await chatMessages.loadFromThread(newThread);

    console.log(
      '[Demo] Created temporary thread and cleared chat messages:',
      newThread.id
    );

    // Hide all UI components during demo
    hide_all_components();

    // Process messages for skip mode if needed
    const processedMessages = skipMode
      ? processDemoMessages(demoMessages, true)
      : demoMessages;

    console.log(processedMessages);

    console.log(
      `[Demo] Using ${processedMessages.length} messages (${skipMode ? 'filtered' : 'original'})`
    );

    // Show demo indicator
    chatMessages.addSystemMessage(
      isSkipToResultMode
        ? '⚡ Demo Mode: Fast-forwarding to result...'
        : '🎬 Demo Mode: Interactive demonstration'
    );

    // Send each message in sequence
    for (let i = 0; i < processedMessages.length; i++) {
      // Check if demo was aborted
      if (isDemoAborted) {
        console.log('[Demo] Demo aborted, stopping message sequence');
        chatMessages.addSystemMessage('⚠️ Demo stopped');
        break;
      }

      const message = processedMessages[i];
      const nextMessage =
        i < processedMessages.length - 1 ? processedMessages[i + 1] : undefined;
      console.log(
        `[Demo] Sending message ${i + 1}/${processedMessages.length}`
      );

      await sendDemoMessage(chatMessages, message, streamingDelay, nextMessage);

      // Add a pause between messages (shorter in skip mode)
      if (i < processedMessages.length - 1) {
        await delay(isSkipToResultMode ? 100 : 1000);
      }
    }

    // Only proceed with completion if not aborted
    if (!isDemoAborted) {
      // If in skip mode, execute all cells at the end
      if (isSkipToResultMode) {
        console.log('[Demo] Skip mode: Executing all cells now');
        await delay(500);
        await executeAllCells();
      }

      // Show completion message
      chatMessages.addSystemMessage('✅ Demo completed!');

      console.log('[Demo] Demo sequence completed');

      // Show all UI components again
      show_all_components();

      // Hide control panel
      hideDemoControlPanel();

      // Delete the temporary thread and create a new thread with the demo messages
      await replaceTempThreadWithDemoThread(newThread.id, demoMessages);
    } else {
      console.log('[Demo] Demo was aborted, skipping completion steps');
      // Still show UI components even if aborted
      show_all_components();
    }
  };

  const handleSkipToResult = async () => {
    console.log('[Demo] Skip to result clicked - switching to instant mode');

    // Set the flag to skip mode immediately
    isSkipToResultMode = true;

    // If demo hasn't started yet, start in skip mode
    if (!demoStarted) {
      await startDemo(true);
    } else {
      // Demo is already running - the flag change will affect ongoing operations
      console.log(
        '[Demo] Demo already running - switching to instant mode for remaining operations'
      );

      // Add a system message to indicate the mode change
      chatMessages.addSystemMessage('⚡ Fast-forwarding to result...');

      // Note: We'll execute all cells at the end when the demo completes
    }
  };

  if (showControlPanel) {
    // Show the control panel with callbacks
    showDemoControlPanel(
      async () => {
        // Try it yourself - create notebook and send first message
        hideDemoControlPanel();
        await tryItYourself(demoMessages);
      },
      handleSkipToResult // Skip to result
    );
  }
  await startDemo(false);
}

/**
 * Create a sample demo sequence from test_history.json
 */
export function createSampleDemoSequence(): DemoMessage[] {
  // Load the test history (should be an array with thread objects)
  if (!testHistory || testHistory.length === 0) {
    console.error('[Demo] No test history available');
    return [];
  }

  // Get the first thread's messages
  const thread = testHistory[0];
  if (!thread || !thread.messages) {
    console.error('[Demo] Invalid thread structure');
    return [];
  }

  const demoMessages: DemoMessage[] = [];

  // Create a map of tool_use_id to tool_result content for easy lookup
  const toolResultMap = new Map<string, string>();

  // First pass: collect all tool results
  for (const message of thread.messages) {
    if (message.role === 'user' && Array.isArray(message.content)) {
      for (const block of message.content) {
        if (
          block.type === 'tool_result' &&
          'tool_use_id' in block &&
          'content' in block
        ) {
          toolResultMap.set(block.tool_use_id, block.content);
        }
      }
    }
  }

  // Convert each message to demo format
  for (const message of thread.messages) {
    // Skip tool_result messages (they're attached to tool_use blocks now)
    if (message.role === 'user' && Array.isArray(message.content)) {
      const hasToolResult = message.content.some(
        (block: any) => block.type === 'tool_result'
      );
      if (hasToolResult) {
        continue; // Skip tool results - they'll be accessed from toolResultMap
      }
    }

    // Skip diff_approval messages (these are internal)
    if (message.role === 'diff_approval') {
      continue;
    }

    // Convert message content to demo format
    let demoContent: string | DemoContentBlock[];

    if (typeof message.content === 'string') {
      demoContent = message.content;
    } else if (Array.isArray(message.content)) {
      // Filter and convert content blocks
      const contentArray = message.content as any[];
      const blocks: (DemoContentBlock | null)[] = contentArray
        .filter(
          (block: any) => block.type === 'text' || block.type === 'tool_use'
        )
        .map((block: any): DemoContentBlock | null => {
          if (block.type === 'text') {
            return {
              type: 'text' as const,
              text: block.text
            };
          } else if (block.type === 'tool_use') {
            // Attach the tool result content to the tool_use block
            const toolResult = toolResultMap.get(block.id);
            return {
              type: 'tool_use' as const,
              id: block.id,
              name: block.name,
              input: block.input,
              result: toolResult // Add the result to the block
            };
          }
          return null;
        });

      demoContent = blocks.filter(
        (block): block is DemoContentBlock => block !== null
      );
    } else {
      // Skip messages with unknown content format
      continue;
    }

    // Create demo message
    const demoMessage: DemoMessage = {
      role: message.role as 'user' | 'assistant',
      content: demoContent
    };

    demoMessages.push(demoMessage);
  }

  return demoMessages;
}

/**
 * Utility function to delay execution
 * When in skip mode, returns immediately
 */
function delay(ms: number): Promise<void> {
  if (isSkipToResultMode) {
    return Promise.resolve();
  }
  return new Promise(resolve => setTimeout(resolve, ms));
}

/**
 * Helper function to get ChatMessages instance from AppState
 */
export function getChatMessages(): ChatMessages | null {
  const chatContainer = AppStateService.getChatContainerSafe();
  return chatContainer?.chatWidget?.messageComponent || null;
}

/**
 * Create a new thread from demo messages and switch to it
 */
async function createThreadFromDemo(
  demoMessages: DemoMessage[]
): Promise<void> {
  const chatContainer = AppStateService.getChatContainerSafe();
  if (!chatContainer || !chatContainer.chatWidget) {
    console.error('[Demo] Chat container not available for thread creation');
    return;
  }

  const chatHistoryManager = chatContainer.chatWidget.chatHistoryManager;
  const chatMessages = chatContainer.chatWidget.messageComponent;
  const currentNotebookId = AppStateService.getCurrentNotebookId();

  if (!currentNotebookId) {
    console.warn('[Demo] No notebook open, cannot create thread');
    return;
  }

  // Convert demo messages to IChatMessage format
  const threadMessages: IChatMessage[] = [];

  for (const demoMsg of demoMessages) {
    const message: IChatMessage = {
      id: uuidv4(),
      role: demoMsg.role,
      content: demoMsg.content as any
    };
    threadMessages.push(message);
  }

  // Create a new thread with these messages
  const newThread: IChatThread = {
    id: chatHistoryManager['generateThreadId'](),
    name: 'Demo: S&P 500 Analysis',
    messages: threadMessages,
    lastUpdated: Date.now(),
    contexts: new Map(),
    message_timestamps: new Map(),
    continueButtonShown: false
  };

  // Add the thread to the notebook
  const threads =
    chatHistoryManager['notebookChats'].get(currentNotebookId) || [];
  threads.unshift(newThread); // Add at the beginning
  chatHistoryManager['notebookChats'].set(currentNotebookId, threads);

  // Save to storage
  await chatHistoryManager['saveNotebookToStorage'](currentNotebookId);

  // Switch to the new thread
  chatHistoryManager['currentThreadId'] = newThread.id;
  await chatHistoryManager['storeCurrentThreadInLocalStorage'](
    currentNotebookId,
    newThread.id
  );

  // Load the thread into the UI
  await chatMessages.loadFromThread(newThread);

  // Update thread name display
  const threadNameDisplay = chatContainer.chatWidget['threadNameDisplay'];
  if (threadNameDisplay) {
    threadNameDisplay.textContent = newThread.name;
  }

  console.log('[Demo] Created and switched to new thread:', newThread.id);
}

/**
 * Replace temporary thread with a new thread using the original chat history from JSON
 */
async function replaceTempThreadWithDemoThread(
  tempThreadId: string,
  demoMessages: DemoMessage[]
): Promise<void> {
  const chatContainer = AppStateService.getChatContainerSafe();
  if (!chatContainer || !chatContainer.chatWidget) {
    console.error('[Demo] Chat container not available for thread replacement');
    return;
  }

  const chatHistoryManager = chatContainer.chatWidget.chatHistoryManager;
  const chatMessages = chatContainer.chatWidget.messageComponent;
  const currentNotebookId = AppStateService.getCurrentNotebookId();

  if (!currentNotebookId) {
    console.warn('[Demo] No notebook open, cannot replace thread');
    return;
  }

  // Get existing threads
  const threads =
    chatHistoryManager['notebookChats'].get(currentNotebookId) || [];

  // Remove the temporary thread
  const filteredThreads = threads.filter(t => t.id !== tempThreadId);

  // Use the original thread from testHistory JSON directly
  if (!testHistory || testHistory.length === 0) {
    console.error('[Demo] No test history available');
    return;
  }

  const originalThread = testHistory[0];
  if (!originalThread || !originalThread.messages) {
    console.error('[Demo] Invalid thread structure in test history');
    return;
  }

  // Create a new thread using the original messages from the JSON
  const newThread: IChatThread = {
    id: chatHistoryManager['generateThreadId'](),
    name: 'Demo: S&P 500 Analysis',
    messages: originalThread.messages,
    lastUpdated: Date.now(),
    contexts: new Map(),
    message_timestamps: new Map(),
    continueButtonShown: false
  };

  // Add the new thread at the beginning
  filteredThreads.unshift(newThread);
  chatHistoryManager['notebookChats'].set(currentNotebookId, filteredThreads);

  // Save to storage
  await chatHistoryManager['saveNotebookToStorage'](currentNotebookId);

  // Switch to the new thread
  chatHistoryManager['currentThreadId'] = newThread.id;
  await chatHistoryManager['storeCurrentThreadInLocalStorage'](
    currentNotebookId,
    newThread.id
  );

  // Load the thread into the UI
  await chatMessages.loadFromThread(newThread);

  // Update thread name display
  const threadNameDisplay = chatContainer.chatWidget['threadNameDisplay'];
  if (threadNameDisplay) {
    threadNameDisplay.textContent = newThread.name;
  }

  console.log(
    '[Demo] Replaced temporary thread with original chat history from JSON:',
    newThread.id
  );
}

/**
 * Show the demo control panel
 */
export function showDemoControlPanel(
  onTryIt: () => void,
  onSkip: () => void
): DemoControlPanel {
  // Clean up existing panel if any
  if (demoControlPanel) {
    demoControlPanel.detach();
  }

  demoControlPanel = new DemoControlPanel(onTryIt, onSkip);
  demoControlPanel.attach();

  return demoControlPanel;
}

/**
 * Hide and cleanup the demo control panel
 */
export function hideDemoControlPanel(): void {
  if (demoControlPanel) {
    demoControlPanel.hide();
    setTimeout(() => {
      demoControlPanel?.detach();
      demoControlPanel = null;
    }, 300);
  }

  // Make sure to re-enable all components when control panel is hidden
  show_all_components();
}

/**
 * Try it yourself! - Create a new notebook and send the first prompt
 */
async function tryItYourself(demoMessages: DemoMessage[]): Promise<void> {
  console.log('[Demo] Try it yourself clicked - aborting demo');

  // Set abort flag to stop the ongoing demo
  isDemoAborted = true;

  // Wait a moment for the demo to stop
  await new Promise(resolve => setTimeout(resolve, 500));

  const chatContainer = AppStateService.getChatContainerSafe();
  if (!chatContainer || !chatContainer.chatWidget) {
    console.error('[Demo] Chat container not available');
    return;
  }

  // Show all UI components when user wants to try it themselves
  show_all_components();

  // Find the first user message
  const firstUserMessage = demoMessages.find(msg => msg.role === 'user');
  if (!firstUserMessage || typeof firstUserMessage.content !== 'string') {
    console.error('[Demo] No valid first user message found');
    return;
  }

  const firstPrompt = firstUserMessage.content;

  // Get the notebook tools service
  const notebookTools = AppStateService.getNotebookTools();
  if (!notebookTools) {
    console.error('[Demo] Notebook tools not available');
    return;
  }

  try {
    // Generate a unique notebook name with timestamp
    const timestamp = new Date()
      .toISOString()
      .replace(/[:.]/g, '-')
      .slice(0, -5);
    const notebookName = `demo-sp500-analysis-${timestamp}.ipynb`;

    // Create a new notebook
    console.log(
      '[Demo] Creating new notebook for interactive demo:',
      notebookName
    );
    const created = await notebookTools.open_notebook({
      path_of_notebook: notebookName,
      create_new: true
    });

    if (!created) {
      throw new Error('Failed to create notebook');
    }

    // Wait a bit for the notebook to fully initialize
    await new Promise(resolve => setTimeout(resolve, 800));

    // Now send the first message
    const chatWidget = chatContainer.chatWidget;
    const inputManager = chatWidget.inputManager;

    // Set the input value
    inputManager.setInputValue(firstPrompt);

    // Send the message
    console.log('[Demo] Sending first message:', firstPrompt);
    await inputManager.sendMessage();

    console.log('[Demo] Interactive demo started successfully');
  } catch (error) {
    console.error('[Demo] Error starting interactive demo:', error);
    alert(
      `Failed to start demo: ${error instanceof Error ? error.message : String(error)}`
    );
  }
}
