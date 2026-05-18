import axios from "axios";

const API_URL = "/api/proxy";

export const api = axios.create({
  baseURL: API_URL,
  timeout: 10000,
});

export interface Lead {
  id: string;
  name: string;
  city: string;
  state: string;
  google_rating: number;
  google_review_count: number;
  website: string;
  email: string;
  phone: string;
  latitude: number;
  longitude: number;
  score: number;
  tier: string;
  confidence: number;
}

export interface AnalyticsSummary {
  total_businesses: number;
  total_scored: number;
  hot_leads: number;
  warm_leads: number;
  cold_leads: number;
  total_outreach: number;
  pending_outreach: number;
  sent_outreach: number;
  replied_outreach: number;
  avg_score: number;
}

export interface Outreach {
  id: string;
  business_id: string;
  to_email: string;
  subject: string;
  body: string;
  status: string;
  sent_at: string;
  opened_at: string;
  replied_at: string;
  created_at: string;
}

export const getLeads = async (tier?: string): Promise<Lead[]> => {
  const params = tier ? { tier } : {};
  const res = await api.get("/leads/", { params });
  return res.data;
};

export const getHotLeads = async (): Promise<Lead[]> => {
  const res = await api.get("/leads/hot");
  return res.data;
};

export const getSummary = async (): Promise<AnalyticsSummary> => {
  const res = await api.get("/analytics/summary");
  return res.data;
};

export const getOutreach = async (): Promise<Outreach[]> => {
  const res = await api.get("/outreach");
  return res.data;
};

export const getScoreDistribution = async () => {
  const res = await api.get("/analytics/scores/distribution");
  return res.data;
};

export const getCities = async () => {
  const res = await api.get("/leads/cities/list");
  return res.data;
};

export const getModelMetadata = async () => {
  const res = await api.get("/model/metadata");
  return res.data;
};
