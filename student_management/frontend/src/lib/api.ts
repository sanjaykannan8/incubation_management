import axios, { AxiosInstance, AxiosResponse } from 'axios';

const API_BASE_URL = 'http://localhost:8000';

export interface Student {
  id: number;
  email: string;
  password_hash: string;
  full_name: string;
  phone: string;
  batch_year?: number;
  department?: string;
  status?: string;
  created_at?: string;
  updated_at?: string;
}

export interface StudentRegistration {
  id: number;
  email: string;
  password_hash: string;
  full_name: string;
  phone: string;
  batch_year?: number;
  department?: string;
}

export interface Mentor {
  id: number;
  email: string;
  password_hash: string;
  full_name: string;
  phone: string;
  title: string;
  expertise: string[];
  available: boolean;
  created_at?: string;
  updated_at?: string;
}

export interface Event {
  id: number;
  title: string;
  description?: string;
  starts_at?: string;
  ends_at?: string;
  location?: string;
  created_by: number; // mentor_id
}

export interface StudentCertificate {
  id: number;
  student_id: number;
  certificate_title: string;
  description?: string;
  issued_by: number; // mentor_id
  certificate_data?: Record<string, unknown>;
  issued_date?: string;
}

export interface LeaderboardEntry {
  id: number;
  student_id: number;
  metric: string;
  score: number;
  context?: Record<string, unknown> | null;
}

export interface Alumni {
  id: number;
  student_id: number;
  graduation_year?: number;
  current_status?: string;
}

export interface Feedback {
  id: number;
  student_id: number;
  feedback_text: string;
  created_at?: string;
}

export interface DatabaseStats {
  total_students: number;
  total_mentors: number;
  total_events: number;
  total_certificates: number;
  total_leaderboard_entries: number;
  total_alumni: number;
  total_feedbacks: number;
}

class ApiService {
  private client: AxiosInstance;

  constructor() {
    this.client = axios.create({
      baseURL: API_BASE_URL,
      headers: {
        'Content-Type': 'application/json',
      },
      timeout: 10000,
    });

    // Add response interceptor for error handling
    this.client.interceptors.response.use(
      (response: AxiosResponse) => response,
      (error) => {
        console.error('API Error:', error.response?.data || error.message);
        throw error;
      }
    );
  }

  // Student endpoints
  async registerStudent(student: StudentRegistration): Promise<{ message: string; student_id: number }> {
    const response = await this.client.post('/students/register', student);
    return response.data;
  }

  async getStudent(id: number): Promise<Student> {
    const response = await this.client.get<Student>(`/students/${id}`);
    return response.data;
  }

  async getAllStudents(): Promise<{ total_students: number; students: Student[] }> {
    const response = await this.client.get('/admin/students/all');
    return response.data;
  }

  async filterStudents(filters: {
    department?: string;
    batch_year?: number;
    status?: string;
    search?: string;
  }): Promise<{ filters: any; results_found: number; students: Student[] }> {
    const params = new URLSearchParams();
    if (filters.department) params.append('department', filters.department);
    if (filters.batch_year) params.append('batch_year', filters.batch_year.toString());
    if (filters.status) params.append('status', filters.status);
    if (filters.search) params.append('search', filters.search);
    
    const response = await this.client.get(`/admin/students/filter?${params.toString()}`);
    return response.data;
  }

  async getStudentDepartments(): Promise<{ departments: string[] }> {
    const response = await this.client.get('/admin/students/departments');
    return response.data;
  }

  async getStudentBatchYears(): Promise<{ batch_years: number[] }> {
    const response = await this.client.get('/admin/students/batch-years');
    return response.data;
  }

  async getStudentStatuses(): Promise<{ statuses: string[] }> {
    const response = await this.client.get('/admin/students/statuses');
    return response.data;
  }

  // Mentor endpoints
  async registerMentor(mentor: Omit<Mentor, 'id' | 'created_at' | 'updated_at'>): Promise<{ message: string; mentor_id: number }> {
    const response = await this.client.post('/mentors/register', mentor);
    return response.data;
  }

  async getMentor(id: number): Promise<Mentor> {
    const response = await this.client.get<Mentor>(`/mentors/${id}`);
    return response.data;
  }

  async getAllMentors(): Promise<{ total_mentors: number; mentors: Mentor[] }> {
    const response = await this.client.get('/admin/mentors/all');
    return response.data;
  }

  // Event endpoints
  async createEvent(event: Omit<Event, 'id'>): Promise<{ message: string; event_id: number }> {
    const response = await this.client.post('/events/create', event);
    return response.data;
  }

  async getEvent(id: number): Promise<Event> {
    const response = await this.client.get<Event>(`/events/${id}`);
    return response.data;
  }

  async getAllEvents(): Promise<{ total_events: number; events: Event[] }> {
    const response = await this.client.get('/admin/events/all');
    return response.data;
  }

  // Certificate endpoints
  async issueCertificate(certificate: Omit<StudentCertificate, 'id'>): Promise<{ message: string; student_certificate_id: number }> {
    const response = await this.client.post('/student_certificates/issue', certificate);
    return response.data;
  }

  async getCertificate(id: number): Promise<StudentCertificate> {
    const response = await this.client.get<StudentCertificate>(`/student_certificates/${id}`);
    return response.data;
  }

  // Leaderboard endpoints
  async addLeaderboardEntry(entry: LeaderboardEntry): Promise<{ message: string; entry_id: number }> {
    const response = await this.client.post('/leaderboard/add', entry);
    return response.data;
  }

  async getLeaderboardEntry(id: number): Promise<LeaderboardEntry> {
    const response = await this.client.get<LeaderboardEntry>(`/leaderboard/${id}`);
    return response.data;
  }

  // Alumni endpoints
  async registerAlumni(alumni: Omit<Alumni, 'id'>): Promise<{ message: string; alumni_id: number }> {
    const response = await this.client.post('/alumni/register', alumni);
    return response.data;
  }

  async getAlumni(id: number): Promise<Alumni> {
    const response = await this.client.get<Alumni>(`/alumni/${id}`);
    return response.data;
  }

  // Feedback endpoints
  async addFeedback(feedback: Omit<Feedback, 'id' | 'created_at'>): Promise<{ message: string; feedback_id: number }> {
    const response = await this.client.post('/feedbacks/add', feedback);
    return response.data;
  }

  async getFeedback(id: number): Promise<Feedback> {
    const response = await this.client.get<Feedback>(`/feedbacks/${id}`);
    return response.data;
  }

  // Admin endpoints
  async getDatabaseInfo(): Promise<Record<string, unknown>> {
    const response = await this.client.get('/admin/database-info');
    return response.data;
  }

  async getAllTables(): Promise<Record<string, unknown>> {
    const response = await this.client.get('/admin/tables');
    return response.data;
  }

  async getDatabaseStatistics(): Promise<DatabaseStats> {
    const response = await this.client.get<DatabaseStats>('/admin/statistics');
    return response.data;
  }
}

export const apiService = new ApiService();
