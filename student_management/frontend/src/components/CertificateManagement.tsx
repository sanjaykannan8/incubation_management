'use client';

import { useState, useEffect } from 'react';
import { apiService, StudentCertificate, Student, Mentor } from '@/lib/api';

export default function CertificateManagement() {
  const [students, setStudents] = useState<Student[]>([]);
  const [mentors, setMentors] = useState<Mentor[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedCertificate, setSelectedCertificate] = useState<StudentCertificate | null>(null);

  // Form state for issuing new certificate
  const [newCertificate, setNewCertificate] = useState({
    student_id: 0,
    certificate_title: '',
    description: '',
    issued_by: 1, // Default mentor ID
    certificate_data: {} as Record<string, unknown>,
  });
  const [jsonInput, setJsonInput] = useState<string>('{}');
  const [viewCertId, setViewCertId] = useState<number | ''>('');

  useEffect(() => {
    fetchStudents();
    fetchMentors();
  }, []);

  const fetchStudents = async () => {
    try {
      setLoading(true);
      const data = await apiService.getAllStudents();
      setStudents(data.students);
      setError(null);
    } catch (err) {
      setError('Failed to fetch students');
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

  const handleIssueCertificate = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      // Parse JSON safely
      let parsedData: Record<string, unknown> = {};
      if (jsonInput && jsonInput.trim().length > 0) {
        try {
          parsedData = JSON.parse(jsonInput);
        } catch (parseErr) {
          setError('Certificate Data must be valid JSON');
          return;
        }
      }

      const certificateData = {
        student_id: newCertificate.student_id,
        certificate_title: newCertificate.certificate_title,
        description: newCertificate.description,
        issued_by: newCertificate.issued_by,
        certificate_data: parsedData,
      };

      await apiService.issueCertificate(certificateData);
      setNewCertificate({
        student_id: 0,
        certificate_title: '',
        description: '',
        issued_by: 1,
        certificate_data: {},
      });
      setJsonInput('{}');
      setError(null);
      // Note: We don't have a get all certificates endpoint, so we can't refresh the list
    } catch (err) {
      setError('Failed to issue certificate');
      console.error(err);
    }
  };

  const handleViewCertificate = async (certificateId: number) => {
    try {
      const certificate = await apiService.getCertificate(certificateId);
      setSelectedCertificate(certificate);
    } catch (err) {
      setError('Failed to fetch certificate details');
      console.error(err);
    }
  };

  const getStudentName = (studentId: number) => {
    const student = students.find(s => s.id === studentId);
    return student ? student.full_name : `Student ${studentId}`;
  };

  const getMentorName = (mentorId: number) => {
    const mentor = mentors.find(m => m.id === mentorId);
    return mentor ? mentor.full_name : `Mentor ${mentorId}`;
  };

  const certificateTypes = [
    'Course Completion',
    'Participation',
    'Leadership',
    'Project Completion',
    'Achievement',
    'Excellence',
    'Technical Skill',
    'Internship',
  ];

  if (loading) {
    return (
      <div className="flex justify-center items-center py-8">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold text-gray-800">Certificate Management</h2>
      </div>

      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
          {error}
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Issue Certificate */}
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold text-gray-800 mb-4">Issue Certificate</h3>
          <form onSubmit={handleIssueCertificate} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700">Student ID</label>
              <input
                type="number"
                value={newCertificate.student_id || ''}
                onChange={(e) => setNewCertificate({ ...newCertificate, student_id: parseInt(e.target.value || '0') })}
                className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="e.g., 1"
                required
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700">Certificate Title</label>
              <select
                value={newCertificate.certificate_title}
                onChange={(e) => setNewCertificate({ ...newCertificate, certificate_title: e.target.value })}
                className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                required
              >
                <option value="">Select type</option>
                {certificateTypes.map((type) => (
                  <option key={type} value={type}>{type}</option>
                ))}
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700">Description (optional)</label>
              <textarea
                value={newCertificate.description}
                onChange={(e) => setNewCertificate({ ...newCertificate, description: e.target.value })}
                className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                rows={3}
                placeholder="Details about the certificate"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700">Issued By (Mentor ID)</label>
              <input
                type="number"
                value={newCertificate.issued_by}
                onChange={(e) => setNewCertificate({ ...newCertificate, issued_by: parseInt(e.target.value || '1') })}
                className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="e.g., 1"
                required
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700">Certificate Data (JSON)</label>
              <textarea
                value={jsonInput}
                onChange={(e) => setJsonInput(e.target.value)}
                className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md font-mono text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                rows={6}
                placeholder='{"grade":"A","course":"AI"}'
              />
            </div>
            <button
              type="submit"
              className="w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700"
            >
              Issue Certificate
            </button>
          </form>
        </div>

        {/* Fetch Certificate */}
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold text-gray-800 mb-4">Fetch Certificate</h3>
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700">Certificate ID</label>
              <input
                type="number"
                value={viewCertId}
                onChange={(e) => setViewCertId(e.target.value === '' ? '' : parseInt(e.target.value))}
                className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                placeholder="e.g., 101"
              />
            </div>
            <button
              onClick={() => {
                if (typeof viewCertId === 'number') handleViewCertificate(viewCertId);
              }}
              className="w-full bg-purple-600 text-white py-2 px-4 rounded-md hover:bg-purple-700"
            >
              View Certificate
            </button>

            {/* Display Area */}
            <div className="mt-4">
              {selectedCertificate ? (
                <div className="rounded-lg border border-gray-200 shadow-sm p-4">
                  <div className="flex items-center justify-between mb-2">
                    <h4 className="font-semibold text-gray-800">Certificate #{selectedCertificate.id}</h4>
                    <span className="text-xs text-gray-500">{selectedCertificate.issued_date ? new Date(selectedCertificate.issued_date).toLocaleString() : ''}</span>
                  </div>
                  <div className="grid grid-cols-2 gap-2 text-sm">
                    <div className="text-gray-500">Student</div>
                    <div className="text-gray-900">{getStudentName(selectedCertificate.student_id)}</div>
                    <div className="text-gray-500">Title</div>
                    <div className="text-gray-900">{selectedCertificate.certificate_title}</div>
                    <div className="text-gray-500">Issued By</div>
                    <div className="text-gray-900">{getMentorName(selectedCertificate.issued_by)}</div>
                    {selectedCertificate.description && (
                      <>
                        <div className="text-gray-500">Description</div>
                        <div className="text-gray-900">{selectedCertificate.description}</div>
                      </>
                    )}
                  </div>
                  {selectedCertificate.certificate_data && (
                    <div className="mt-3">
                      <div className="text-sm font-medium text-gray-700 mb-1">Certificate Data</div>
                      <pre className="bg-gray-50 rounded p-3 text-xs overflow-auto">
{`${JSON.stringify(selectedCertificate.certificate_data, null, 2)}`}
                      </pre>
                    </div>
                  )}
                </div>
              ) : (
                <div className="text-sm text-gray-500">Enter an ID and click View to see details.</div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
