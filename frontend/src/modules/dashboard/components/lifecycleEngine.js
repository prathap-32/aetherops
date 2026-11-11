// frontend/src/modules/dashboard/components/lifecycleEngine.js
/**
 * Resolves the AetherOps workspace lifecycle state (L00 - L12)
 * based on confirmed backend data: user onboarding state, projects, environments, connections, and deployments.
 */
export function resolveLifecycleState({ user = null, projects = [], environments = [], connections = { git: [], cloud: [] }, deployments = [] }) {
  // Authoritative first-time user check from backend user profile
  if (user && user.has_seen_welcome === 0) {
    return 'L00_FIRST_VISIT';
  }

  if (projects.length === 0 && environments.length === 0) {
    return 'L01_NO_PROJECTS';
  }

  // Check for critical operational failures / attention required
  const hasFailedDeployment = deployments.some(d => d.status === 'FAILED' || d.status === 'ERROR');
  if (hasFailedDeployment) {
    return 'L11_ATTENTION_REQUIRED';
  }

  if (projects.length > 0 && environments.length === 0) {
    return 'L03_ENVIRONMENT_SETUP';
  }

  const hasCloudOrGit = (connections.git?.length || 0) > 0 || (connections.cloud?.length || 0) > 0;
  if (projects.length > 0 && environments.length > 0 && !hasCloudOrGit) {
    return 'L04_CONNECTION_SETUP';
  }

  const hasActiveDeployments = deployments.some(d => d.status === 'RUNNING' || d.status === 'DEPLOYING');
  if (hasActiveDeployments) {
    return 'L09_DEPLOYMENT_IN_PROGRESS';
  }

  const hasSuccessfulDeployments = deployments.some(d => d.status === 'SUCCESS');
  if (hasSuccessfulDeployments) {
    return 'L10_ACTIVE_OPERATIONS';
  }

  if (projects.length > 0 && environments.length > 0 && hasCloudOrGit) {
    return 'L08_PRE_DEPLOYMENT';
  }

  return 'L12_RETURNING_USER';
}

export function getNextBestAction(lifecycleState, { projects = [], environments = [], connections = { git: [], cloud: [] } }) {
  switch (lifecycleState) {
    case 'L00_FIRST_VISIT':
    case 'L01_NO_PROJECTS':
      return {
        title: 'Create Your First Project Workspace',
        description: 'Set up an isolated project boundary to begin infrastructure synthesis and deployment.',
        actionLabel: 'Create Project',
        targetView: 'projects',
        targetPath: '/project-environment',
      };
    case 'L03_ENVIRONMENT_SETUP':
      return {
        title: 'Provision Target Environment',
        description: 'Configure your first target environment (Development, Staging, or Production) for deployment.',
        actionLabel: 'Configure Environment',
        targetView: 'environments',
        targetPath: '/project-environment',
      };
    case 'L04_CONNECTION_SETUP':
      return {
        title: 'Connect Cloud & Git Credentials',
        description: 'Securely link your GitHub repository and AWS IAM role to enable code analysis and provisioning.',
        actionLabel: 'Connect Accounts',
        targetView: 'source_cloud',
        targetPath: '/source-connection',
      };
    case 'L08_PRE_DEPLOYMENT':
      return {
        title: 'Run AI Architecture & Dry Run',
        description: 'Analyze your codebase, generate AWS architecture, and run pre-deployment risk evaluation.',
        actionLabel: 'Start Architecture Planning',
        targetView: 'architecture_studio',
        targetPath: '/architecture-studio',
      };
    case 'L11_ATTENTION_REQUIRED':
      return {
        title: 'Resolve Deployment Failure',
        description: 'Review state inventory and approval execution logs to remediate the failed operational run.',
        actionLabel: 'Inspect Deployments',
        targetView: 'deployments',
        targetPath: '/deployment',
      };
    default:
      return {
        title: 'Synthesize & Deploy Infrastructure',
        description: 'Review generated Terraform configurations and execute approved cloud deployments.',
        actionLabel: 'View Infrastructure Synthesizer',
        targetView: 'iac',
        targetPath: '/terraform',
      };
  }
}
