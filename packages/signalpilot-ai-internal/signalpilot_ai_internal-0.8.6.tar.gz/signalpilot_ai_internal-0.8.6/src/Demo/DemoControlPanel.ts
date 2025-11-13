import { Widget } from '@lumino/widgets';

/**
 * Demo Control Panel - A floating control panel for demo mode
 * Provides options to either try the demo interactively or skip to results
 */
export class DemoControlPanel extends Widget {
  private containerDiv: HTMLDivElement;
  private tryItButton: HTMLButtonElement;
  private skipButton: HTMLButtonElement;
  private onTryItCallback: () => void;
  private onSkipCallback: () => void;

  constructor(onTryIt: () => void, onSkip: () => void) {
    super();

    this.onTryItCallback = onTryIt;
    this.onSkipCallback = onSkip;

    this.addClass('sage-ai-demo-control-panel');

    // Create container
    this.containerDiv = document.createElement('div');
    this.containerDiv.className = 'sage-ai-demo-control-container';

    // Create title
    const title = document.createElement('div');
    title.className = 'sage-ai-demo-control-title';
    title.textContent = 'Replay Mode';

    // Create button container
    const buttonContainer = document.createElement('div');
    buttonContainer.className = 'sage-ai-demo-control-buttons';

    // Create "Try it yourself!" button
    this.tryItButton = document.createElement('button');
    this.tryItButton.className =
      'sage-ai-demo-control-button sage-ai-demo-control-try';
    this.tryItButton.innerHTML = `
      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <path d="M12 2L2 7l10 5 10-5-10-5z"></path>
        <path d="M2 17l10 5 10-5"></path>
        <path d="M2 12l10 5 10-5"></path>
      </svg>
      <span>Try it yourself!</span>
    `;
    this.tryItButton.onclick = () => this.handleTryIt();

    // Create "Skip to result" button
    this.skipButton = document.createElement('button');
    this.skipButton.className =
      'sage-ai-demo-control-button sage-ai-demo-control-skip';
    this.skipButton.innerHTML = `
      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <polygon points="5 3 19 12 5 21 5 3"></polygon>
        <line x1="19" y1="3" x2="19" y2="21"></line>
      </svg>
      <span>Skip to result</span>
    `;
    this.skipButton.onclick = () => this.handleSkip();

    buttonContainer.appendChild(this.tryItButton);
    buttonContainer.appendChild(this.skipButton);

    this.containerDiv.appendChild(title);
    this.containerDiv.appendChild(buttonContainer);

    this.node.appendChild(this.containerDiv);
  }

  private handleTryIt(): void {
    this.disableButtons();
    this.onTryItCallback();
  }

  private handleSkip(): void {
    this.disableButtons();
    this.onSkipCallback();
  }

  private disableButtons(): void {
    this.tryItButton.disabled = true;
    this.skipButton.disabled = true;
    this.tryItButton.style.opacity = '0.5';
    this.skipButton.style.opacity = '0.5';
    this.tryItButton.style.cursor = 'not-allowed';
    this.skipButton.style.cursor = 'not-allowed';
  }

  /**
   * Show the control panel
   */
  public show(): void {
    this.node.style.display = 'flex';
    this.node.style.opacity = '0';

    // Animate in
    requestAnimationFrame(() => {
      this.node.style.transition = 'opacity 0.3s ease';
      this.node.style.opacity = '1';
    });
  }

  /**
   * Hide the control panel
   */
  public hide(): void {
    this.node.style.transition = 'opacity 0.3s ease';
    this.node.style.opacity = '0';

    setTimeout(() => {
      this.node.style.display = 'none';
    }, 300);
  }

  /**
   * Attach the control panel to the document
   */
  public attach(): void {
    document.body.appendChild(this.node);
    this.show();
  }

  /**
   * Detach the control panel from the document
   */
  public detach(): void {
    if (this.node.parentNode) {
      this.node.parentNode.removeChild(this.node);
    }
  }
}
