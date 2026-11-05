// Fictional sample data from the Figma concept. Replace with API calls once the backend exists.
export const EVENTS = {
  'EVT-0412': 'Fare protest, Central Sq.',
  'EVT-0418': 'Ministry press briefing',
  'EVT-0431': 'Road blockade, Harbor Rd.',
}

export const NARRATIVES = ['#FareFairness', '#OfficialResponse', '#EconomicImpact']

export const PERSONA_TYPES = ['Local resident', 'Journalist', 'Media org', 'Government', 'Civil society', 'Commentator']

export const POSTS = [
  { id: 'PST-0001', name: 'Rosa Delmar', handle: 'rosad_cs', time: '14:02', type: 'Local resident', color: '#2f7a4f',
    text: 'Third day walking to work. The new fare is half my daily lunch money. Central Square is packed again this morning.',
    event: 'EVT-0412', narrative: '#FareFairness', replies: 14, reposts: 31, likes: 120 },
  { id: 'PST-0002', name: 'Harbor Daily', handle: 'harbordaily', time: '13:55', type: 'Media org', color: '#6a3fb0',
    text: 'Live: Several hundred protesters gather at Central Square for a third day over the transit fare increase. Ministry briefing expected at 16:00.',
    event: 'EVT-0412', narrative: '#FareFairness', replies: 42, reposts: 210, likes: 388 },
  { id: 'PST-0003', name: 'Ministry of Transport', handle: 'mot_official', time: '13:40', type: 'Government', color: '#334155',
    text: 'The fare adjustment funds overdue maintenance on 40% of the bus fleet. Reduced fares for students and seniors remain in place.',
    event: 'EVT-0418', narrative: '#OfficialResponse', replies: 96, reposts: 54, likes: 71 },
  { id: 'PST-0004', name: 'Teo Marsh', handle: 'teomarsh_news', time: '13:21', type: 'Journalist', color: '#1f5fb8',
    text: 'Road blockade on Harbor Rd. is now affecting freight into the port. Drivers I spoke with say they support the protest but are losing a day of pay.',
    event: 'EVT-0431', narrative: '#EconomicImpact', replies: 8, reposts: 47, likes: 95 },
  { id: 'PST-0005', name: 'Commuters United', handle: 'commutersunited', time: '12:58', type: 'Civil society', color: '#9a4a12',
    text: 'We are asking the ministry to publish the full maintenance budget before the increase takes effect. Transparency first.',
    event: 'EVT-0418', narrative: '#OfficialResponse', replies: 23, reposts: 88, likes: 160 },
  { id: 'PST-0006', name: 'Dana Okafor', handle: 'danaok', time: '12:30', type: 'Commentator', color: '#8e2b5a',
    text: 'Every fare fight in this city goes the same way: blockade, briefing, small concession. Watch the student discount get expanded by Friday.',
    event: 'EVT-0412', narrative: '#FareFairness', replies: 31, reposts: 19, likes: 204 },
]
