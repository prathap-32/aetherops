// frontend/src/modules/dashboard/components/lifecycleEngine.js
/**
 * Resolves the AetherOps dynamic welcome state (State A, B, C, D)
 * and Next Best Action based on actual persisted database records.
 */
export function resolveLifecycleState({ user = null, projects = [], environments = [], connections = { git: [], cloud: [] }, deployments = [] }) {
  if (projects.length === 0) {
    return 'STATE_A_NEW_USER';
  }

  const hasGit = (connections.git?.length || 0) > 0;
  const hasCloud = (connections.cloud?.length || 0) > 0;

  if (!hasGit || !hasCloud) {
    return 'STATE_B_CONNECTION_SETUP';
  }

  if (hasGit && hasCloud) {
    return 'STATE_C_READY_FOR_ANALYSIS';
  }

  return 'STATE_D_RETURNING_USER';
}

export function getNextBestAction(lifecycleState, { projects = [], environments = [], connections = { git: [], cloud: [] } }) {
  switch (lifecycleState) {
    case 'STATE_A_NEW_USER':
      return {
        title: 'Create Your First Project Workspace',
        description: 'Set up an isolated project boundary to begin infrastructure synthesis and deployment.',
        actionLabel: 'Create Project',
        targetView: 'projects',
        targetPath: '/project-environment',
      };
    case 'STATE_B_CONNECTION_SETUP':
      return {
        title: 'Connect Cloud & Git Credentials',
        description: 'Your workspace is ready. Connect your source repository and cloud account to continue.',
        actionLabel: 'Connect Accounts',
        targetView: 'source_cloud',
        targetPath: '/source-connection',
      };
    case 'STATE_C_READY_FOR_ANALYSIS':
      return {
        title: 'Continue with Source Analysis',
        description: 'Your source and cloud connections are ready. Continue with source analysis.',
        actionLabel: 'Continue',
        targetView: 'repo_analyzer',
        targetPath: '/source-analysis',
      };
    case 'STATE_D_RETURNING_USER':
    default:
      return {
        title: 'Manage Projects & Workspaces',
        description: 'Pick up where you left off and continue managing your projects.',
        actionLabel: 'View Projects',
        targetView: 'projects',
        targetPath: '/project-environment',
      };
  }
}
