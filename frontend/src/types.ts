export type JsonValue =
  | string
  | number
  | boolean
  | null
  | JsonValue[]
  | { [key: string]: JsonValue };

export interface ApiClientConfig {
  apiBaseUrl: string;
  apiKey: string;
  requestId: string;
}

export interface ApiResult<T> {
  data: T;
  requestId: string;
  status: number;
}

export interface VideoJobResponse {
  job_id: string;
  status: string;
  video_id: string;
  run_name: string;
  run_dir: string;
  message: string;
  output_dir?: string | null;
  summary_path?: string | null;
  artifact_paths?: Record<string, string> | null;
  error?: string | null;
  created_at?: string | null;
  updated_at?: string | null;
  started_at?: string | null;
  finished_at?: string | null;
  model_path?: string | null;
  video_path?: string | null;
  conf?: number | null;
  imgsz?: number | null;
  device?: string | null;
}

export interface VideoAnalyzePayload {
  video_id: string;
  run_name: string;
  source?: string;
  video_path?: string;
  model_path?: string;
  conf: number;
  imgsz: number;
  device: string;
  run_dir?: string;
}

export interface BadCasePayload {
  module: string;
  case_type: string;
  video_id: string;
  image_name: string;
  frame_index: string;
  expected_result: string;
  actual_result: string;
  root_cause: string;
  tags: string;
  reviewer_note: string;
}

export interface BadCaseRecord extends BadCasePayload {
  case_id: string;
  created_at: string;
  timestamp_sec?: string;
  track_id?: string;
  snapshot_path?: string;
  added_to_eval_set?: string;
}

export interface DetectionResult {
  class_id: number;
  class_name: string;
  confidence: number;
  bbox: {
    xmin: number;
    ymin: number;
    xmax: number;
    ymax: number;
  };
}

export interface PredictResponse {
  image_name: string;
  image_size: Record<string, number>;
  model_path: string;
  confidence_threshold: number;
  image_size_requested: number;
  device: string;
  num_detections: number;
  detections: DetectionResult[];
}
