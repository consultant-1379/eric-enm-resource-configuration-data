const history = Object.freeze([
  {
    version: '1.0.0',
    changes: [
      'Mocked Customizations',
      'Workloads CPU & Memory',
      'Storage requirements',
      'Mocked Node Calculator wizard'
    ]
  },
  {
    version: '1.1.0',
    changes: [
      'Image information page',
      'Version selection',
      'Anti-affinity column',
      'Expandable workload details (containers)',
      'Node Calculator (Naive Algorithm)',
      'Cluster visualization',
      'Redesigned Overview Page'
    ]
  },
  {
    version: '1.2.0',
    changes: [
      'Sortable columns in CPU &amp; Memory page',
      'Variant selection, improved data-model',
      'Removed node profiles',
      'Simulated Kubernetes scheduling to determine the number of worker node',
      'Improved cluster visualization',
      'Highlight workloads, navigate to details',
      'Change Log'
    ]
  },
  {
    version: '1.2.1',
    changes: [
      'Fixed scheduler node scoring',
      'Fixed optimal node count calculation',
      'Best-effort soft-anti-affinity'
    ]
  },
  {
    version: '1.3.0',
    changes: [
      'Small bug-fixes',
      'Improved numeric input on Node Calculator page',
      'Images are sorted by their name',
      'Modernized Version History',
      'Improved data model: record field descriptions',
      'Improved tables: common filtering, sorting, expansion logic',
      'Reorganized structure to follow K8s logic (CPU & Memory → Workloads, Storage → PVCs)'
    ]
  },
  {
    version: '1.4.0',
    changes: [
      'Soft pod-anti-affinity',
      'Pod disruption budget',
      'Improved JSON model',
      'More robust chart parsing',
      'Improved the display of Workload details',
      'Selectable target audience',
      'Named versions, filtered by target audience',
      'Scheduler now uses "limits" instead of "requests"'
    ]
  },
  {
    version: '1.4.1',
    changes: [
      'Reworked Node Calculator'
    ]
  },
  {
    version: '1.4.2',
    changes: [
      'Several bug-fixes',
      'Reimplemented PDU recommendations for node-sizing'
    ]
  },
  {
    version: '1.5.1',
    changes: [
      'Updates for build automation'
    ]
  },
  {
    version: '1.6.1',
    changes: [
      'Add summary of k8s workloads',
      'Migrate logical calculations from web to gen part'
    ]
  },
  {
    version: '1.7.1',
    changes: [
      'Introduction to Resource overview tab of client/cluster software and resource requirements'
    ]
  },
  {
    version: '1.7.2',
    changes: [
      'Updates for domain name resourceconfigurationdata.internal.ericsson.com',
      'Updates to support https using SSL certificate'
    ]
  },
  {
    version: '1.7.3',
    changes: [
      'Removed prefix column in Images page',
      'Displays only image name and tag under pods in workload section',
      'Removed Affinity and Pod Disruption Budget columns in workloads page',
      'Removed "Secret stuff, nothing to see here button" in version history',
      'Removed "Issues & Ideas" button in the homepage',
      'Removed Storage Class, App Name columns',
      'Removed Preview word from "Preview Simulated ENM Deployment" title in Node Calculator',
      'Renamed Instances column to Replicas under PVC & Ephemeral section in PVC page',
      'Removed "x" in Replicas values under Workload and PVC pages',
      'Pods can be sorted in workloads based on Kind',
      'PVCs can be sorted based on there type in PVC page',
      'Changed to Size Requests, Size Limits(instead of Size Require, Size Limit) under Ephemeral storage section in PVC page'
    ]
  },
  {
    version: '1.7.4',
    changes: [
      'Included CronJobs in workloads under workloads page',
    ]
  },
  {
    version: '1.7.5',
    changes: [
      'Added info icon for tooltip messages on Resource overview page',
      'Replaced use of RAM to Memory on Resource overview page',
      'Removed use of size on Ephemeral Storage table on PVCs page',
      'Removed Docker version from Cluster Software Requirements on Resource overview page',
      'Updated software versions'
    ]
  },
  {
    version: '1.7.6',
    changes: [
      'Fixed version dropdown issue',
    ]
  },
  {
    version: '1.8.1',
    changes: [
      'Added Docker registry requirements to Resource Overview page'
    ]
  },
  {
    version: '1.8.2',
    changes: [
      'Added Landing Page for DeploymentSetup'
    ]
  },
  {
    version: '1.8.3',
    changes: [
      'Added Update Strategy to Workloads page'
    ]
  },
  {
    version: '1.9.1',
    changes: [
      'Moved overview calculation from generator to font end',
      'Remove the Jobs from the overall calculation.'
    ]
  },
  {
    version: '1.9.2',
    changes: [
      'Made Node Calculator only available when PDU is selected'
    ]
  },
  {
    version: '1.9.3',
    changes: [
      'Populating N/A for Anti-affinity and PDB empty fields'
    ]
  },
  {
    version: '1.9.4',
    changes: [
      'Introduced BUR related information on PVCs and Resource Overview pages'
    ]
  },
  {
    version: '1.9.5',
    changes: [
      'Changed layout of Resource Overview page'
    ]
  },
  {
    version: '1.9.6',
    changes: [
      'Introduce EBS-LS non-mandatory applications optionality to RCD Deployment setup'
    ]
  },
  {
    version: '1.10.1',
    changes: [
      'Fixed update of workloads page when an optional value pack is disabled'
    ]
  },
  {
    version: '1.10.2',
    changes: [
      'Split PDU and CU RCD.'
    ]
  },
  {
    version: '1.10.3',
    changes: [
      'Introduce EBS-M non-mandatory applications optionality to RCD Deployment setup'
    ]
  },
  {
    version: '1.11.1',
    changes: [
      'Usability improvements on Deployment Setup page',
      'Sort the version dropdown list',
      'Remove caching of product set data in the browser',
      'RWO total count on the Resource Overview page updated'
    ]
  },
  {
    version: '1.12.1',
    changes: [
      'Changed the values for ephemeral storage from GiB to MiB',
      'Min. worker nodes calculation does not include 1 extra worker node for extra-large environment',
      'Updated tooltip information for Minimum Worker Nodes in Resource Overview page'
    ]
  },
  {
    version: '1.13.1',
    changes: [
      'Displays ENM Rlease Versions from latest to oldest.'
    ]
  },
  {
    version: '1.13.2',
    changes: [
      'Navigate to Resource Overview automatically on successful deployment setup.'
    ]
  },
  {
    version: '1.14.1',
    changes: [
      'Add other requirements section to Resource Overview page.'
    ]
  },
  {
    version: '1.15.1',
    changes: [
      'Removed "Warning this tool is still under development!" message.',
      'Changed the internal RCD page header to "Internal Cloud Native ENM Resource Configuration Data"',
      'Substituted "Docker Registry" with "Container Registry" in Resource Overview page'
    ]
  },
  {
    version: '1.15.2',
    changes: [
      'Added validation for workloads.'
    ]
  },
  {
    version: '1.15.3',
    changes: [
      'Updated PVCs page to Storage.',
      'Move "Ephemeral Storage" overview to "Storage Requirements" section.'
    ]
  },
  {
    version: '1.15.4',
    changes: [
      'Updated RWO total requirements to factor in number of instances.',
    ]
  },
  {
    version: '1.15.5',
    changes: [
      'Increased font size for title in resource overview page',
      'Updated switch toggle in Deployment Setup Page',
    ]
  },
  {
    version: '1.15.6',
    changes: [
      'Removed Console Logging',
    ]
  },
  {
    version: '1.15.7',
    changes: [
      'Remove caching of index.json in the browser',
    ]
  },
  {
    version: '1.16.1',
    changes: [
      'Disabled version on the External/CU RCD UI and enabled it on Internal/PDU RCD UI',
    ]
  },
  {
    version: '1.16.2',
    changes: [
      'Add excel export option for internal use',
    ]
  },
  {
    version: '1.16.3',
    changes: [
      'Remove SG column from Exported excel file.',
    ]
  },
  {
    version: '1.17.1',
    changes: [
      'Introduction of tool to compare different ENM versions ',
    ]
  },
  {
    version: '1.17.2',
    changes: [
      'Introduce build automation for RCD.',
    ]
  },
  {
    version: '1.17.3',
    changes: [
      'Fix for compare page where too many decimal places for Storage Requirements: RWO and RWX' +
      ' getting printed to the screen for difference between from and to states',
    ]
  },
  {
    version: '1.17.4',
    changes: [
      'Setup deployment button should only be visible when the model is prepared.',
    ]
  },
  {
    version: '1.18.1',
    changes: [
      'Fix for compare page when ENM version has no other requirements values and' +
      'fix when for compare button is pressed multiple times it was adding new values',
    ]
  },
  {
    version: '1.19.1',
    changes: [
      'Added option to choose between different IP address types to Deployment Setup and Compare Releases',
    ]
  },
  {
    version: '1.20.1',
    changes: [
      'Introduced view of resource requirements for Jobs and removed ENM references from overview',
    ]
  },
  {
    version: '1.22.2',
    changes: [
      'Added RedisCluster kind pods to be tracked in the workloads page',
    ]
  },
  {
    version: '1.23.1',
    changes: [
      'Added FAN to internal RCD as optional value',
    ]
  },
  {
    version: '1.24.1',
    changes: [
      'Added support for multiple IP address types.',
    ]
  },
  {
    version: '1.25.1',
    changes: [
      'Use APIs to do business logic.',
    ]
  }
  ,
  {
    version: '1.25.2',
    changes: [
      'Update API url.',
    ]
  },
  {
    version: '1.27.1',
    changes: [
      'Removal of Software requirements section.',
    ]
  },
  {
    version: '1.28.1',
    changes: [
      'Updated API to include IP version',
      'Changed number of EricIngresses and Services in Overview to vary based on IP version',
    ]
  },
  {
    version: '1.28.2',
    changes: [
      'Added support for IPv6_EXT IP version'
    ]
  },
  {
    version: '1.29.1',
    changes: [
      'Fix for IP version dropdown being visible for product sets with only the IPv4 option'
    ]
  },
  {
    version: '1.30.1',
    changes: [
      'RCD UI enhancements to support EIC product offering'
    ]
  },
  {
    version: '1.31.2',
    changes: [
      'Introduced WinFIOL OPS AXE Mediation non-mandatory application optionality to RCD Deployment setup'
    ]
  },
  {
    version: '1.31.3',
    changes: [
      'For RCD EIC product offering, UI label changed for disk storage space in container registry requirements section'
    ]
  },
  {
    version: '1.31.4',
    changes: [
      'Introduced non-mandatory services optionality to RCD Deployment setup and display the services under a non mandatory services section'
    ]
  },
  {
    version: '1.31.5',
    changes: [
      'For RCD EIC product offering, added a tooltip for number of pods in K8s overview section in overview page'
    ]
  },
  {
    version: '1.32.1',
    changes: [
      'MSAPGFM workloads should not be removed when "AXE node Support (Mediation Winfiol and OPS)" is enabled in deployment setup since introduction of non-mandatory services.',
      'Ephemeral storage should not be displayed in the Storage view when an application is disabled.'
    ]
  },
  {
    version: '1.33.1',
    changes: [
      'Updates to application names and descriptions to better align with product description text.'
    ]
  },
  {
    version: '1.34.1',
    changes: [
      'Remove code to hide File Access NBI application from the external UI.'
    ]
  },
  {
    version: '1.35.1',
    changes: [
      'For RCD EIC, few UI elements are removed in application worker nodes section in the resource overview page.'
    ]
  },
  {
    version: '1.36.1',
    changes: [
      'For RCD cENM view, added Requests and Limits for both CPU and Memory.'
    ]
  },
  {
    version: '1.36.2',
    changes: [
      'For RCD EIC, a separate section Storage Requirements For Backups added in Resource Overview page.'
    ]
  },
  {
    version: '1.36.3',
    changes: [
      'For RCD EIC, data source changes made in section Storage Requirements For Backups in Resource Overview page.'
    ]
  },
  {
    version: '1.36.4',
    changes: [
      'For RCD cENM view, added panel Cluster Recommendation.'
    ]
  },
  {
    version: '1.36.5',
    changes: [
      'For RCD cENM, fixed Excel export to properly account for non-mandatory services.'
    ]
  }
].reverse());

export default Object.freeze({
  history,
  currentVersion: history[0].version
});
