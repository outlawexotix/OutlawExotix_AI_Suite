const vscode = require('vscode');
const { exec } = require('child_process');
const path = require('path');
const fs = require('fs');

/**
 * War Room Extension for Google Antigravity
 * Integrates Outlaw Exotix AI agents into Antigravity IDE
 */

let outputChannel;
let memoryWatcher;

function activate(context) {
    console.log('War Room extension is now active!');

    // Create output channel
    outputChannel = vscode.window.createOutputChannel('War Room');
    context.subscriptions.push(outputChannel);

    // Register all commands
    registerCommands(context);

    // Start memory file watcher
    startMemoryWatcher(context);

    // Show welcome message
    vscode.window.showInformationMessage('War Room agents ready for deployment!');
}

function registerCommands(context) {
    // Overwatch Agent - Strategic Analysis
    context.subscriptions.push(
        vscode.commands.registerCommand('warroom.summonOverwatch', async () => {
            await summonAgent('overwatch', 'Strategic Analysis');
        })
    );

    // Ethical Hacker - Security Audit
    context.subscriptions.push(
        vscode.commands.registerCommand('warroom.summonEthicalHacker', async () => {
            await summonAgent('ethical-hacker', 'Security Audit');
        })
    );

    // Code Auditor - Quality Review
    context.subscriptions.push(
        vscode.commands.registerCommand('warroom.summonCodeAuditor', async () => {
            await summonAgent('code-auditor', 'Code Quality Review');
        })
    );

    // Apex Analyst - Research
    context.subscriptions.push(
        vscode.commands.registerCommand('warroom.summonApexAnalyst', async () => {
            await summonAgent('apex-analyst', 'Research & Analysis');
        })
    );

    // Chief of Staff - Delegation
    context.subscriptions.push(
        vscode.commands.registerCommand('warroom.summonChiefOfStaff', async () => {
            await summonAgent('chief-of-staff', 'Task Delegation');
        })
    );

    // Open War Room Console
    context.subscriptions.push(
        vscode.commands.registerCommand('warroom.openConsole', () => {
            openWarRoomConsole();
        })
    );

    // Run Test Suite
    context.subscriptions.push(
        vscode.commands.registerCommand('warroom.runTests', () => {
            runTestSuite();
        })
    );

    // View Shared Memory
    context.subscriptions.push(
        vscode.commands.registerCommand('warroom.viewMemory', () => {
            viewSharedMemory();
        })
    );
}

async function summonAgent(agentName, agentDescription) {
    const config = vscode.workspace.getConfiguration('warroom');
    const binPath = config.get('binPath', './bin');

    // Get task from user
    const task = await vscode.window.showInputBox({
        prompt: `Enter task for ${agentDescription} agent`,
        placeHolder: `e.g., Analyze this codebase for vulnerabilities`,
        validateInput: (value) => {
            return value.trim().length === 0 ? 'Task cannot be empty' : null;
        }
    });

    if (!task) {
        return; // User cancelled
    }

    // Get current file context if editor is open
    const editor = vscode.window.activeTextEditor;
    let contextInfo = '';
    if (editor) {
        const document = editor.document;
        const selection = editor.selection;

        if (!selection.isEmpty) {
            const selectedText = document.getText(selection);
            contextInfo = `\n\nSelected Code:\n${selectedText}`;
        }

        contextInfo = `File: ${document.fileName}${contextInfo}`;
    }

    const fullTask = `${task}${contextInfo ? `\n\nContext: ${contextInfo}` : ''}`;

    // Show progress
    await vscode.window.withProgress({
        location: vscode.ProgressLocation.Notification,
        title: `Summoning ${agentDescription}...`,
        cancellable: false
    }, async (progress) => {
        // Determine script extension based on platform
        const scriptExt = process.platform === 'win32' ? '.ps1' : '.sh';
        const agentScript = path.join(binPath, `agent${scriptExt}`);

        // Build command
        let command;
        if (process.platform === 'win32') {
            command = `powershell -ExecutionPolicy Bypass -File "${agentScript}" -Name "${agentName}" -p "${fullTask.replace(/"/g, '\\"')}"`;
        } else {
            command = `bash "${agentScript}" "${agentName}" -p "${fullTask.replace(/"/g, '\\"')}"`;
        }

        outputChannel.clear();
        outputChannel.appendLine(`=== ${agentDescription.toUpperCase()} ===`);
        outputChannel.appendLine(`Task: ${task}`);
        outputChannel.appendLine(`Agent: ${agentName}`);
        outputChannel.appendLine('');
        outputChannel.show(true);

        return new Promise((resolve) => {
            exec(command, { cwd: vscode.workspace.rootPath }, (error, stdout, stderr) => {
                if (error) {
                    outputChannel.appendLine(`ERROR: ${error.message}`);
                    vscode.window.showErrorMessage(`Agent execution failed: ${error.message}`);
                } else {
                    outputChannel.appendLine(stdout);
                    if (stderr) {
                        outputChannel.appendLine(`\nWarnings:\n${stderr}`);
                    }

                    // Show completion notification
                    vscode.window.showInformationMessage(
                        `${agentDescription} completed!`,
                        'View Memory'
                    ).then(selection => {
                        if (selection === 'View Memory') {
                            viewSharedMemory();
                        }
                    });
                }
                resolve();
            });
        });
    });
}

function openWarRoomConsole() {
    const config = vscode.workspace.getConfiguration('warroom');
    const pythonPath = config.get('pythonPath', 'python');
    const toolsPath = config.get('toolsPath', './tools');

    const terminal = vscode.window.createTerminal({
        name: 'War Room Console',
        cwd: vscode.workspace.rootPath
    });

    terminal.show();
    terminal.sendText(`${pythonPath} ${path.join(toolsPath, 'war_room.py')}`);
}

function runTestSuite() {
    const terminal = vscode.window.createTerminal({
        name: 'War Room Tests',
        cwd: vscode.workspace.rootPath
    });

    terminal.show();

    if (process.platform === 'win32') {
        terminal.sendText('.\\run_tests.ps1 -Coverage');
    } else {
        terminal.sendText('./run_tests.sh --coverage');
    }
}

function viewSharedMemory() {
    const config = vscode.workspace.getConfiguration('warroom');
    const memoryFile = config.get('memoryFile', './PROJECT_MEMORY.md');
    const memoryPath = path.join(vscode.workspace.rootPath, memoryFile);

    if (fs.existsSync(memoryPath)) {
        vscode.workspace.openTextDocument(memoryPath).then(doc => {
            vscode.window.showTextDocument(doc, vscode.ViewColumn.Beside);
        });
    } else {
        vscode.window.showWarningMessage('Shared memory file not found. Agents will create it on first use.');
    }
}

function startMemoryWatcher(context) {
    const config = vscode.workspace.getConfiguration('warroom');
    const memoryFile = config.get('memoryFile', './PROJECT_MEMORY.md');
    const memoryPath = path.join(vscode.workspace.rootPath, memoryFile);

    if (!fs.existsSync(memoryPath)) {
        return; // File doesn't exist yet
    }

    const autoShow = config.get('autoShowMemory', true);

    memoryWatcher = fs.watch(memoryPath, (eventType) => {
        if (eventType === 'change' && autoShow) {
            // Debounce updates
            setTimeout(() => {
                vscode.window.showInformationMessage(
                    'Shared memory updated',
                    'View'
                ).then(selection => {
                    if (selection === 'View') {
                        viewSharedMemory();
                    }
                });
            }, 500);
        }
    });

    context.subscriptions.push({
        dispose: () => {
            if (memoryWatcher) {
                memoryWatcher.close();
            }
        }
    });
}

function deactivate() {
    if (outputChannel) {
        outputChannel.dispose();
    }
    if (memoryWatcher) {
        memoryWatcher.close();
    }
}

module.exports = {
    activate,
    deactivate
};
