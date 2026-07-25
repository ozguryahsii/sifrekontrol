/** Python API (sifrekontrol serve) sözleşmesi. */

export interface StrengthResult {
  score: 0 | 1 | 2 | 3 | 4;
  guesses_log10: number;
  crack_time_offline_fast: string;
  crack_time_online: string;
  warnings: string[];
  suggestions: string[];
  engine: "zxcvbn" | "fallback";
}

export interface Requirement {
  description: string;
  passed: boolean | null;
  detail: string;
}

export interface RegulationResult {
  id: string;
  name: string;
  scope: string;
  passed: boolean | null;
  requirements: Requirement[];
}

export interface CheckResult {
  length: number;
  strength: StrengthResult;
  breach_count: number | null;
  regulations: RegulationResult[];
}

export interface DatasetStatus {
  data_dir: string;
  groups_present: number;
  groups_total: number;
  complete: boolean;
  records: number;
  size_bytes: number;
  updated_at: string | null;
  last_sync: string | null;
}
