#!/usr/bin/env bash
cd frontend_code_analysis
reflex run --env prod --single-port --frontend-port "$PORT"
