'use client';

import { useState, useEffect } from 'react';
import { apiService, DatabaseStats } from '@/lib/api';

export default function AdminDashboard() {
  const [stats, setStats] = useState<DatabaseStats | null>(null);
  const [dbInfo, setDbInfo] = useState<Record<string, unknown> | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      
      // Try to get database statistics, but provide fallback if it fails
      let statsData: DatabaseStats;
      try {
        statsData = await apiService.getDatabaseStatistics();
      } catch (statErr) {
        console.warn('Statistics endpoint failed, using fallback data:', statErr);
        // Provide fallback statistics matching the interface
        statsData = {
          total_students: 0,
          total_mentors: 0,
          total_events: 0,
          total_certificates: 0,
          total_leaderboard_entries: 0,
          total_alumni: 0,
          total_feedbacks: 0
        };
      }
      
      // Get database info
      const dbInfoData = await apiService.getDatabaseInfo();
      
      setStats(statsData);
      setDbInfo(dbInfoData);
      setError(null);
    } catch (err) {
      setError('Failed to fetch dashboard data');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center py-8">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-red-600 text-center py-4">
        {error}
        <button
          onClick={fetchDashboardData}
          className="ml-2 text-blue-600 hover:underline"
        >
          Retry
        </button>
      </div>
    );
  }

  const statCards = stats ? [
    { title: 'Total Students', value: stats.total_students, icon: '👨‍🎓', color: 'bg-blue-500' },
    { title: 'Total Mentors', value: stats.total_mentors, icon: '👨‍🏫', color: 'bg-green-500' },
    { title: 'Total Events', value: stats.total_events, icon: '📅', color: 'bg-purple-500' },
    { title: 'Certificates Issued', value: stats.total_certificates, icon: '🏆', color: 'bg-yellow-500' },
    { title: 'Leaderboard Entries', value: stats.total_leaderboard_entries, icon: '🏅', color: 'bg-red-500' },
    { title: 'Alumni', value: stats.total_alumni, icon: '🎓', color: 'bg-indigo-500' },
    { title: 'Total Feedback', value: stats.total_feedbacks, icon: '💬', color: 'bg-pink-500' },
  ] : [];

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold text-gray-800">Dashboard Overview</h2>
        <button
          onClick={fetchDashboardData}
          className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 flex items-center space-x-2"
        >
          <span>🔄</span>
          <span>Refresh</span>
        </button>
      </div>

      {/* Statistics Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
        {statCards.map((card, index) => (
          <div key={index} className="bg-white rounded-lg shadow-md p-6 border-l-4 border-gray-200">
            <div className="flex items-center">
              <div className={`${card.color} rounded-full p-3 mr-4`}>
                <span className="text-white text-xl">{card.icon}</span>
              </div>
              <div>
                <p className="text-sm font-medium text-gray-600">{card.title}</p>
                <p className="text-2xl font-bold text-gray-900">{card.value}</p>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Database Information */}
      {dbInfo && (
        <div className="bg-white rounded-lg shadow-md p-6">
          <h3 className="text-xl font-semibold text-gray-800 mb-4">Database Information</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <p><span className="font-medium">Database:</span> {(dbInfo?.database_name as string) || 'studentmanagement'}</p>
              <p><span className="font-medium">Host:</span> {(dbInfo?.host as string) || 'localhost'}</p>
              <p><span className="font-medium">Port:</span> {(dbInfo?.port as string) || '5432'}</p>
            </div>
            <div className="space-y-2">
              <p><span className="font-medium">Status:</span> 
                <span className="ml-2 px-2 py-1 bg-green-100 text-green-800 rounded-full text-xs">
                  Connected
                </span>
              </p>
              <p><span className="font-medium">Last Updated:</span> {new Date().toLocaleString()}</p>
            </div>
          </div>
        </div>
      )}

      {/* Quick Actions */}
      <div className="bg-white rounded-lg shadow-md p-6">
        <h3 className="text-xl font-semibold text-gray-800 mb-4">Quick Actions</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <button className="p-4 border border-gray-200 rounded-lg hover:bg-gray-50 text-center">
            <div className="text-2xl mb-2">👨‍🎓</div>
            <div className="text-sm font-medium">Add Student</div>
          </button>
          <button className="p-4 border border-gray-200 rounded-lg hover:bg-gray-50 text-center">
            <div className="text-2xl mb-2">👨‍🏫</div>
            <div className="text-sm font-medium">Add Mentor</div>
          </button>
          <button className="p-4 border border-gray-200 rounded-lg hover:bg-gray-50 text-center">
            <div className="text-2xl mb-2">📅</div>
            <div className="text-sm font-medium">Create Event</div>
          </button>
          <button className="p-4 border border-gray-200 rounded-lg hover:bg-gray-50 text-center">
            <div className="text-2xl mb-2">🏆</div>
            <div className="text-sm font-medium">Issue Certificate</div>
          </button>
        </div>
      </div>
    </div>
  );
}
