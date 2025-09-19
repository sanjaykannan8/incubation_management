'use client';

import { useState } from 'react';
import { apiService } from '@/lib/api';

export default function ApiPlayground() {
  const [active, setActive] = useState<'leaderboard' | 'alumni' | 'feedback'>('leaderboard');

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold text-gray-800">API Tester</h2>
      </div>

      <div className="border-b border-gray-200">
        <nav className="flex space-x-6" aria-label="Sub Tabs">
          {[
            { id: 'leaderboard', label: 'Leaderboard' },
            { id: 'alumni', label: 'Alumni' },
            { id: 'feedback', label: 'Feedback' },
          ].map((t) => (
            <button
              key={t.id}
              onClick={() => setActive(t.id as any)}
              className={`py-3 px-1 border-b-2 text-sm font-medium ${
                active === (t.id as any)
                  ? 'border-blue-600 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              {t.label}
            </button>
          ))}
        </nav>
      </div>

      {active === 'leaderboard' && <LeaderboardTester />}
      {active === 'alumni' && <AlumniTester />}
      {active === 'feedback' && <FeedbackTester />}
    </div>
  );
}

export function LeaderboardTester() {
  const [lastId, setLastId] = useState<number | null>(null);
  const [serverMsg, setServerMsg] = useState<string | null>(null);
  return (
    <div className="bg-white rounded-lg shadow p-6 max-w-xl">
      <h3 className="text-lg font-semibold text-gray-800 mb-4">Add Leaderboard Entry</h3>
      <form className="space-y-3" onSubmit={async (e) => {
        e.preventDefault();
        const form = e.target as HTMLFormElement;
        const data = Object.fromEntries(new FormData(form) as any) as any;
        // Generate a safe integer ID (< 2,147,483,647)
        const safeRandomId = Math.floor(100000 + Math.random() * 900000);
        try {
          const res = await apiService.addLeaderboardEntry({
            id: parseInt(data.entry_id || '0') || safeRandomId,
            student_id: parseInt(data.student_id),
            metric: data.activity_type,
            score: parseInt(data.points),
            context: data.description ? { description: data.description } : null,
          });
          form.reset();
          setServerMsg('Leaderboard entry added');
          setLastId(res.entry_id || null);
        } catch (err: any) {
          const detail = err?.response?.data?.detail || 'Request failed';
          setServerMsg(`Add failed: ${detail}`);
        }
      }}>
        <input name="entry_id" type="number" placeholder="Entry ID (optional)" className="w-full px-3 py-2 border rounded" />
        <input name="student_id" type="number" placeholder="Student ID" className="w-full px-3 py-2 border rounded" required />
        <input name="activity_type" placeholder="Activity Type" className="w-full px-3 py-2 border rounded" required />
        <input name="points" type="number" placeholder="Score" className="w-full px-3 py-2 border rounded" required />
        <input name="description" placeholder="Description (optional)" className="w-full px-3 py-2 border rounded" />
        <button className="w-full bg-blue-600 text-white py-2 rounded">Add Entry</button>
      </form>

      <div className="mt-6">
        <h4 className="font-medium text-gray-800 mb-2">Get Entry</h4>
        <div className="flex gap-2">
          <input id="leaderboardIdPg" type="number" placeholder="Entry ID" className="flex-1 px-3 py-2 border rounded" defaultValue={lastId ?? undefined} />
          <button className="px-3 py-2 bg-purple-600 text-white rounded" onClick={async () => {
            const id = parseInt((document.getElementById('leaderboardIdPg') as HTMLInputElement).value || '');
            try {
              if (!isNaN(id)) {
                await apiService.getLeaderboardEntry(id);
                setServerMsg('Fetched entry successfully');
              }
            } catch (err: any) {
              const detail = err?.response?.data?.detail || 'Not found';
              setServerMsg(`Get failed: ${detail}`);
            }
          }}>Get</button>
        </div>
        {serverMsg && <p className="mt-3 text-sm text-gray-600">{serverMsg}</p>}
        <p className="mt-2 text-xs text-gray-500">Tip: Use a valid Student ID from the Students tab; the same (student_id, metric) pair must be unique.</p>
      </div>
    </div>
  );
}

export function AlumniTester() {
  return (
    <div className="bg-white rounded-lg shadow p-6 max-w-xl">
      <h3 className="text-lg font-semibold text-gray-800 mb-4">Register Alumni</h3>
      <form className="space-y-3" onSubmit={async (e) => {
        e.preventDefault();
        const form = e.target as HTMLFormElement;
        const data = Object.fromEntries(new FormData(form) as any) as any;
        await apiService.registerAlumni({
          student_id: parseInt(data.student_id),
          graduation_year: data.graduation_year ? parseInt(data.graduation_year) : undefined,
          current_status: data.current_status || undefined,
        });
        form.reset();
      }}>
        <input name="student_id" type="number" placeholder="Student ID" className="w-full px-3 py-2 border rounded" required />
        <input name="graduation_year" type="number" placeholder="Graduation Year" className="w-full px-3 py-2 border rounded" />
        <input name="current_status" placeholder="Current Status" className="w-full px-3 py-2 border rounded" />
        <button className="w-full bg-blue-600 text-white py-2 rounded">Register Alumni</button>
      </form>

      <div className="mt-6">
        <h4 className="font-medium text-gray-800 mb-2">Get Alumni</h4>
        <div className="flex gap-2">
          <input id="alumniIdPg" type="number" placeholder="Alumni ID" className="flex-1 px-3 py-2 border rounded" />
          <button className="px-3 py-2 bg-purple-600 text-white rounded" onClick={async () => {
            const id = parseInt((document.getElementById('alumniIdPg') as HTMLInputElement).value || '');
            if (!isNaN(id)) await apiService.getAlumni(id);
          }}>Get</button>
        </div>
      </div>
    </div>
  );
}

export function FeedbackTester() {
  return (
    <div className="bg-white rounded-lg shadow p-6 max-w-xl">
      <h3 className="text-lg font-semibold text-gray-800 mb-4">Add Feedback</h3>
      <form className="space-y-3" onSubmit={async (e) => {
        e.preventDefault();
        const form = e.target as HTMLFormElement;
        const data = Object.fromEntries(new FormData(form) as any) as any;
        await apiService.addFeedback({
          student_id: parseInt(data.student_id),
          feedback_text: data.feedback_text,
        });
        form.reset();
      }}>
        <input name="student_id" type="number" placeholder="Student ID" className="w-full px-3 py-2 border rounded" required />
        <input name="feedback_text" placeholder="Your feedback" className="w-full px-3 py-2 border rounded" required />
        <button className="w-full bg-blue-600 text-white py-2 rounded">Add Feedback</button>
      </form>

      <div className="mt-6">
        <h4 className="font-medium text-gray-800 mb-2">Get Feedback</h4>
        <div className="flex gap-2">
          <input id="feedbackIdPg" type="number" placeholder="Feedback ID" className="flex-1 px-3 py-2 border rounded" />
          <button className="px-3 py-2 bg-purple-600 text-white rounded" onClick={async () => {
            const id = parseInt((document.getElementById('feedbackIdPg') as HTMLInputElement).value || '');
            if (!isNaN(id)) await apiService.getFeedback(id);
          }}>Get</button>
        </div>
      </div>
    </div>
  );
}


