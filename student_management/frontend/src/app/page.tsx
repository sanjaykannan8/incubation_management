'use client';

import { useState } from 'react';
import StudentManagement from '@/components/StudentManagement';
import MentorManagement from '@/components/MentorManagement';
import EventManagement from '@/components/EventManagement';
import CertificateManagement from '@/components/CertificateManagement';
import AdminDashboard from '@/components/AdminDashboard';
import { LeaderboardTester, AlumniTester, FeedbackTester } from '@/components/ApiPlayground';

export default function Home() {
  const [activeTab, setActiveTab] = useState('dashboard');

  const tabs = [
    { id: 'dashboard', name: 'Dashboard', icon: '📊' },
    { id: 'students', name: 'Students', icon: '👨‍🎓' },
    { id: 'mentors', name: 'Mentors', icon: '👨‍🏫' },
    { id: 'events', name: 'Events', icon: '📅' },
    { id: 'certificates', name: 'Certificates', icon: '🏆' },
    { id: 'leaderboard', name: 'Leaderboard', icon: '🏅' },
    { id: 'alumni', name: 'Alumni', icon: '🎓' },
    { id: 'feedback', name: 'Feedback', icon: '💬' },
  ];

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="container mx-auto px-4 py-8">
        <header className="mb-8">
          <h1 className="text-4xl font-bold text-gray-800 mb-2">
            Student Management System
          </h1>
          <p className="text-gray-600">
            Comprehensive platform for managing students, mentors, events, and certificates
          </p>
        </header>

        <div className="bg-white rounded-lg shadow-md">
          <div className="border-b border-gray-200">
            <nav className="flex space-x-8" aria-label="Tabs">
              {tabs.map((tab) => (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`py-4 px-1 border-b-2 font-medium text-sm flex items-center space-x-2 ${
                    activeTab === tab.id
                      ? 'border-blue-500 text-blue-600'
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  }`}
                >
                  <span>{tab.icon}</span>
                  <span>{tab.name}</span>
                </button>
              ))}
            </nav>
          </div>

          <div className="p-6">
            {activeTab === 'dashboard' && <AdminDashboard />}
            {activeTab === 'students' && <StudentManagement />}
            {activeTab === 'mentors' && <MentorManagement />}
            {activeTab === 'events' && <EventManagement />}
            {activeTab === 'certificates' && <CertificateManagement />}
            {activeTab === 'leaderboard' && <LeaderboardTester />}
            {activeTab === 'alumni' && <AlumniTester />}
            {activeTab === 'feedback' && <FeedbackTester />}
          </div>
        </div>
      </div>
    </div>
  );
}
