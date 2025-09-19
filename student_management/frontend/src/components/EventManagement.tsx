'use client';

import { useState, useEffect } from 'react';
import { apiService, Event, Mentor } from '@/lib/api';

export default function EventManagement() {
  const [events, setEvents] = useState<Event[]>([]);
  const [mentors, setMentors] = useState<Mentor[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showAddForm, setShowAddForm] = useState(false);
  const [selectedEvent, setSelectedEvent] = useState<Event | null>(null);

  // Form state for adding new event
  const [newEvent, setNewEvent] = useState({
    title: '',
    description: '',
    starts_at: '',
    ends_at: '',
    location: '',
    created_by: 1, // Default mentor ID
  });

  useEffect(() => {
    fetchEvents();
    fetchMentors();
  }, []);

  const fetchEvents = async () => {
    try {
      setLoading(true);
      const data = await apiService.getAllEvents();
      setEvents(data.events);
      setError(null);
    } catch (err) {
      setError('Failed to fetch events');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const fetchMentors = async () => {
    try {
      const data = await apiService.getAllMentors();
      setMentors(data.mentors);
    } catch (err) {
      console.error('Failed to fetch mentors:', err);
    }
  };

  const handleAddEvent = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const toIsoUtc = (value: string) => (value ? new Date(value).toISOString() : undefined);

      const eventData = {
        title: newEvent.title,
        description: newEvent.description,
        // Normalize local datetime input to ISO UTC to avoid timezone shifts
        starts_at: toIsoUtc(newEvent.starts_at),
        ends_at: toIsoUtc(newEvent.ends_at),
        location: newEvent.location,
        created_by: newEvent.created_by,
      };

      await apiService.createEvent(eventData);
      setNewEvent({
        title: '',
        description: '',
        starts_at: '',
        ends_at: '',
        location: '',
        created_by: 1,
      });
      setShowAddForm(false);
      fetchEvents();
    } catch (err) {
      setError('Failed to add event');
      console.error(err);
    }
  };

  const handleViewEvent = async (eventId: number) => {
    try {
      const event = await apiService.getEvent(eventId);
      setSelectedEvent(event);
    } catch (err) {
      setError('Failed to fetch event details');
      console.error(err);
    }
  };

  const formatDateTime = (datetime: string) => {
    if (!datetime) return { date: 'N/A', time: 'N/A' };
    const date = new Date(datetime);
    return {
      date: date.toLocaleDateString(),
      time: date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    };
  };

  const getMentorName = (mentorId: number) => {
    const mentor = mentors.find(m => m.id === mentorId);
    return mentor ? mentor.full_name : `Mentor ${mentorId}`;
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center py-8">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold text-gray-800">Event Management</h2>
        <div className="space-x-2">
          <button
            onClick={fetchEvents}
            className="px-4 py-2 bg-gray-600 text-white rounded-md hover:bg-gray-700"
          >
            Refresh
          </button>
          <button
            onClick={() => setShowAddForm(true)}
            className="px-4 py-2 bg-purple-600 text-white rounded-md hover:bg-purple-700"
          >
            Add Event
          </button>
        </div>
      </div>

      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
          {error}
        </div>
      )}

      {/* Add Event Form Modal */}
      {showAddForm && (
        <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
          <div className="relative top-10 mx-auto p-5 border w-96 shadow-lg rounded-md bg-white max-h-screen overflow-y-auto">
            <h3 className="text-lg font-bold text-gray-900 mb-4">Add New Event</h3>
            <form onSubmit={handleAddEvent} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700">Event Title</label>
                <input
                  type="text"
                  required
                  value={newEvent.title}
                  onChange={(e) => setNewEvent({ ...newEvent, title: e.target.value })}
                  className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700">Description</label>
                <textarea
                  value={newEvent.description}
                  onChange={(e) => setNewEvent({ ...newEvent, description: e.target.value })}
                  className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                  rows={3}
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700">Start Date & Time</label>
                <input
                  type="datetime-local"
                  value={newEvent.starts_at}
                  onChange={(e) => setNewEvent({ ...newEvent, starts_at: e.target.value })}
                  className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700">End Date & Time</label>
                <input
                  type="datetime-local"
                  value={newEvent.ends_at}
                  onChange={(e) => setNewEvent({ ...newEvent, ends_at: e.target.value })}
                  className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700">Location</label>
                <input
                  type="text"
                  value={newEvent.location}
                  onChange={(e) => setNewEvent({ ...newEvent, location: e.target.value })}
                  className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700">Created By (Mentor)</label>
                <select
                  value={newEvent.created_by}
                  onChange={(e) => setNewEvent({ ...newEvent, created_by: parseInt(e.target.value) })}
                  className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                >
                  {mentors.map((mentor) => (
                    <option key={mentor.id} value={mentor.id}>
                      {mentor.full_name}
                    </option>
                  ))}
                </select>
              </div>
              <div className="flex space-x-2">
                <button
                  type="submit"
                  className="flex-1 bg-purple-600 text-white py-2 px-4 rounded-md hover:bg-purple-700"
                >
                  Add Event
                </button>
                <button
                  type="button"
                  onClick={() => setShowAddForm(false)}
                  className="flex-1 bg-gray-600 text-white py-2 px-4 rounded-md hover:bg-gray-700"
                >
                  Cancel
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Event Details Modal */}
      {selectedEvent && (
        <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
          <div className="relative top-20 mx-auto p-5 border w-96 shadow-lg rounded-md bg-white">
            <h3 className="text-lg font-bold text-gray-900 mb-4">Event Details</h3>
            <div className="space-y-2">
              <p><strong>ID:</strong> {selectedEvent.id}</p>
              <p><strong>Title:</strong> {selectedEvent.title}</p>
              <p><strong>Description:</strong> {selectedEvent.description || 'No description'}</p>
              <p><strong>Starts:</strong> {selectedEvent.starts_at ? formatDateTime(selectedEvent.starts_at).date + ' at ' + formatDateTime(selectedEvent.starts_at).time : 'Not set'}</p>
              <p><strong>Ends:</strong> {selectedEvent.ends_at ? formatDateTime(selectedEvent.ends_at).date + ' at ' + formatDateTime(selectedEvent.ends_at).time : 'Not set'}</p>
              <p><strong>Location:</strong> {selectedEvent.location || 'Not specified'}</p>
              <p><strong>Created By:</strong> {getMentorName(selectedEvent.created_by)}</p>
            </div>
            <button
              onClick={() => setSelectedEvent(null)}
              className="mt-4 w-full bg-gray-600 text-white py-2 px-4 rounded-md hover:bg-gray-700"
            >
              Close
            </button>
          </div>
        </div>
      )}

      {/* Events Table */}
      <div className="bg-white rounded-lg shadow-md overflow-hidden">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                ID
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Title
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Start Date & Time
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Location
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Created By
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Actions
              </th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {events.map((event) => {
              const startDateTime = event.starts_at ? formatDateTime(event.starts_at) : { date: 'N/A', time: 'N/A' };
              return (
                <tr key={event.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {event.id}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                    {event.title}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    <div>
                      <div>{startDateTime.date}</div>
                      <div className="text-gray-500">{startDateTime.time}</div>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {event.location || 'Not specified'}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {getMentorName(event.created_by)}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                    <button
                      onClick={() => handleViewEvent(event.id)}
                      className="text-purple-600 hover:text-purple-900"
                    >
                      View
                    </button>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>

        {events.length === 0 && (
          <div className="text-center py-8 text-gray-500">
            No events found
          </div>
        )}
      </div>
    </div>
  );
}
