# CoreView3D

**A modern, open-source web-based 3D viewer for mining drillhole data**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![React](https://img.shields.io/badge/react-18.0+-61dafb.svg)](https://reactjs.org/)

---

## What is CoreView3D ?

A free web-based mining visualization software.

## Quick Start for Devs

### Prerequisites

- Python 3.11+
- Node.js 18+
- [uv](https://github.com/astral-sh/uv) (Python package manager)

### Backend Setup

```bash
cd backend

# Install dependencies with uv
uv pip install -e .

# Run development server
uv run uvicorn app.main:app --reload --port 8000
```

Backend will be available at `http://localhost:8000`

### Frontend Setup

```bash
cd frontend

npm install

npm run dev
```

Frontend will be available at `http://localhost:5173`

### Test with Sample Data

1. Start both backend and frontend
2. Open `http://localhost:5173`
3. Import the example CSV files from `data/examples`
4. Explore your 3D drillhole visualization!

## Data Format

CoreView3D expects standard mining CSV formats:

### Collar Table (Required)
```csv
Hole_ID,East,North,Elevation,Max_Depth,Azimuth,Dip
DH001,450000,6250000,1250,150.5,0,-60
```

### Survey Table (Optional but recommended)
```csv
Hole_ID,Depth,Azimuth,Dip
DH001,0,0,-60
DH001,50,2,-61
```

### Interval Tables (Optional - Assays, Lithology, etc.)
```csv
Hole_ID,From,To,Lithology,Au_ppm,Cu_pct
DH001,0,25.5,Granite,0.05,0.02
DH001,25.5,78.3,Schist,2.35,0.45
```

## Contributing

Contributions are welcome! Please read our [Contributing Guide](CONTRIBUTING.md) first.

### Development Workflow

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Inspired by the open-source geoscience community
- Built with modern web technologies
- Thanks to all contributors

## 📧 Contact

Created by **Bruno Chaintreuil** - [GitHub](https://github.com/bruno-chaintreuil)

Project Link: [https://github.com/bruno-chaintreuil/CoreView3D](https://github.com/bruno-chaintreuil/CoreView3D)