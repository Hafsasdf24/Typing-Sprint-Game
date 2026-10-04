/**
 * Typing Sprint - Interactive WPM History Chart
 * High-DPI Canvas with smooth neon bezier spline, glow gradients, and hover tooltips.
 */

export class WpmChart {
  constructor(canvasElement, tooltipElement) {
    this.canvas = canvasElement;
    this.ctx = canvasElement.getContext('2d');
    this.tooltip = tooltipElement;
    this.data = [];
    this.points = [];
    this.hoveredIndex = -1;
    this.activeFilter = 'all'; // 'all', '10', '25', '50'

    this.initEvents();
  }

  initEvents() {
    this.handleMouseMove = this.onMouseMove.bind(this);
    this.handleMouseLeave = this.onMouseLeave.bind(this);

    this.canvas.addEventListener('mousemove', this.handleMouseMove);
    this.canvas.addEventListener('mouseleave', this.handleMouseLeave);

    // Resize observer to keep chart sharp on window resize
    this.resizeObserver = new ResizeObserver(() => {
      this.render();
    });
    this.resizeObserver.observe(this.canvas.parentElement);
  }

  setData(historyArray, filter = null) {
    if (filter) this.activeFilter = filter;
    let list = [...historyArray];

    if (this.activeFilter === '10') {
      list = list.slice(-10);
    } else if (this.activeFilter === '25') {
      list = list.slice(-25);
    } else if (this.activeFilter === '50') {
      list = list.slice(-50);
    }

    this.data = list;
    this.render();
  }

  onMouseMove(e) {
    if (!this.points || this.points.length === 0) return;

    const rect = this.canvas.getBoundingClientRect();
    const mouseX = e.clientX - rect.left;
    const mouseY = e.clientY - rect.top;

    // Find closest point by X coordinate
    let closestIdx = -1;
    let minDistance = Infinity;

    this.points.forEach((pt, idx) => {
      const dist = Math.hypot(pt.x - mouseX, pt.y - mouseY);
      if (dist < 45 && dist < minDistance) {
        minDistance = dist;
        closestIdx = idx;
      }
    });

    if (closestIdx !== -1) {
      this.hoveredIndex = closestIdx;
      this.showTooltip(this.points[closestIdx], this.data[closestIdx]);
      this.render();
    } else if (this.hoveredIndex !== -1) {
      this.hoveredIndex = -1;
      this.hideTooltip();
      this.render();
    }
  }

  onMouseLeave() {
    this.hoveredIndex = -1;
    this.hideTooltip();
    this.render();
  }

  showTooltip(pt, record) {
    if (!this.tooltip || !record) return;

    const listLabel = record.wordList ? record.wordList.toUpperCase() : 'STANDARD';
    const diffLabel = record.difficulty ? record.difficulty.toUpperCase() : 'NORMAL';

    this.tooltip.innerHTML = `
      <div class="tooltip-header">
        <span class="tooltip-date">${record.dateFormatted || 'Session'}</span>
        <span class="tooltip-badge">${diffLabel} • ${listLabel}</span>
      </div>
      <div class="tooltip-stats">
        <div class="tooltip-stat">
          <span class="label">SPEED</span>
          <span class="val wpm-val">${record.wpm} <small>WPM</small></span>
        </div>
        <div class="tooltip-stat">
          <span class="label">ACCURACY</span>
          <span class="val acc-val">${record.accuracy}%</span>
        </div>
        <div class="tooltip-stat">
          <span class="label">SCORE</span>
          <span class="val pts-val">${record.score || 0}</span>
        </div>
      </div>
    `;

    this.tooltip.style.display = 'block';
    
    // Position tooltip safely within container boundaries
    const containerRect = this.canvas.parentElement.getBoundingClientRect();
    const tooltipWidth = 190;
    let left = pt.x + 12;
    if (left + tooltipWidth > containerRect.width) {
      left = pt.x - tooltipWidth - 12;
    }
    let top = Math.max(10, pt.y - 65);

    this.tooltip.style.left = `${left}px`;
    this.tooltip.style.top = `${top}px`;
  }

  hideTooltip() {
    if (this.tooltip) {
      this.tooltip.style.display = 'none';
    }
  }

  render() {
    const dpr = window.devicePixelRatio || 1;
    const rect = this.canvas.getBoundingClientRect();
    const width = rect.width;
    const height = rect.height;

    if (width === 0 || height === 0) return;

    this.canvas.width = width * dpr;
    this.canvas.height = height * dpr;
    this.ctx.resetTransform?.();
    this.ctx.scale(dpr, dpr);

    const ctx = this.ctx;
    ctx.clearRect(0, 0, width, height);

    const padding = { top: 35, right: 35, bottom: 45, left: 55 };
    const chartW = width - padding.left - padding.right;
    const chartH = height - padding.top - padding.bottom;

    if (!this.data || this.data.length === 0) {
      this.renderEmptyState(width, height);
      return;
    }

    // Determine scale bounds
    const wpms = this.data.map(d => d.wpm || 0);
    const maxDataWpm = Math.max(...wpms, 40);
    const yMax = Math.ceil((maxDataWpm * 1.25) / 20) * 20; // Round to nearest 20
    const yMin = 0;

    // Draw Grid Lines & Y Axis Labels
    ctx.lineWidth = 1;
    ctx.strokeStyle = 'rgba(255, 255, 255, 0.07)';
    ctx.fillStyle = 'rgba(255, 255, 255, 0.45)';
    ctx.font = '11px "Space Grotesk", sans-serif';
    ctx.textAlign = 'right';
    ctx.textBaseline = 'middle';

    const ySteps = 5;
    for (let i = 0; i <= ySteps; i++) {
      const val = Math.round(yMin + (yMax - yMin) * (i / ySteps));
      const y = padding.top + chartH - (chartH * (i / ySteps));

      ctx.beginPath();
      ctx.setLineDash([4, 6]);
      ctx.moveTo(padding.left, y);
      ctx.lineTo(padding.left + chartW, y);
      ctx.stroke();
      ctx.setLineDash([]);

      ctx.fillText(`${val} WPM`, padding.left - 10, y);
    }

    // Calculate Coordinates for Points
    this.points = [];
    const count = this.data.length;

    this.data.forEach((rec, idx) => {
      const x = count === 1 
        ? padding.left + chartW / 2 
        : padding.left + (chartW * (idx / (count - 1)));
      const wpmVal = rec.wpm || 0;
      const normalizedY = (wpmVal - yMin) / (yMax - yMin);
      const y = padding.top + chartH - (chartH * Math.max(0, Math.min(1, normalizedY)));
      this.points.push({ x, y, wpm: wpmVal });
    });

    // Draw Average WPM reference line
    const avgWpm = Math.round(wpms.reduce((a, b) => a + b, 0) / count);
    const avgY = padding.top + chartH - (chartH * ((avgWpm - yMin) / (yMax - yMin)));
    ctx.beginPath();
    ctx.strokeStyle = 'rgba(255, 190, 11, 0.45)';
    ctx.lineWidth = 1.5;
    ctx.setLineDash([6, 6]);
    ctx.moveTo(padding.left, avgY);
    ctx.lineTo(padding.left + chartW, avgY);
    ctx.stroke();
    ctx.setLineDash([]);

    // Average label
    ctx.fillStyle = '#ffbe0b';
    ctx.textAlign = 'left';
    ctx.fillText(`Avg: ${avgWpm} WPM`, padding.left + chartW - 75, avgY - 9);

    // Draw Gradient Area Fill under spline
    if (this.points.length > 1) {
      const areaGrad = ctx.createLinearGradient(0, padding.top, 0, padding.top + chartH);
      areaGrad.addColorStop(0, 'rgba(0, 245, 212, 0.28)');
      areaGrad.addColorStop(0.6, 'rgba(121, 40, 202, 0.12)');
      areaGrad.addColorStop(1, 'rgba(0, 0, 0, 0)');

      ctx.beginPath();
      ctx.moveTo(this.points[0].x, padding.top + chartH);
      ctx.lineTo(this.points[0].x, this.points[0].y);

      // Curve through points
      for (let i = 0; i < this.points.length - 1; i++) {
        const p0 = this.points[i];
        const p1 = this.points[i + 1];
        const mx = (p0.x + p1.x) / 2;
        ctx.bezierCurveTo(mx, p0.y, mx, p1.y, p1.x, p1.y);
      }

      ctx.lineTo(this.points[this.points.length - 1].x, padding.top + chartH);
      ctx.closePath();
      ctx.fillStyle = areaGrad;
      ctx.fill();
    }

    // Draw Glowing Spline Line
    ctx.save();
    ctx.shadowColor = '#00f5d4';
    ctx.shadowBlur = 12;
    ctx.strokeStyle = '#00f5d4';
    ctx.lineWidth = 3;
    ctx.lineCap = 'round';
    ctx.lineJoin = 'round';

    ctx.beginPath();
    if (this.points.length === 1) {
      ctx.arc(this.points[0].x, this.points[0].y, 5, 0, Math.PI * 2);
    } else {
      ctx.moveTo(this.points[0].x, this.points[0].y);
      for (let i = 0; i < this.points.length - 1; i++) {
        const p0 = this.points[i];
        const p1 = this.points[i + 1];
        const mx = (p0.x + p1.x) / 2;
        ctx.bezierCurveTo(mx, p0.y, mx, p1.y, p1.x, p1.y);
      }
      ctx.stroke();
    }
    ctx.restore();

    // Draw Dots on Points
    this.points.forEach((pt, idx) => {
      const isHovered = (this.hoveredIndex === idx);

      ctx.save();
      if (isHovered) {
        // Vertical scanline
        ctx.beginPath();
        ctx.strokeStyle = 'rgba(0, 245, 212, 0.4)';
        ctx.lineWidth = 1;
        ctx.setLineDash([3, 3]);
        ctx.moveTo(pt.x, padding.top);
        ctx.lineTo(pt.x, padding.top + chartH);
        ctx.stroke();
        ctx.setLineDash([]);

        // Highlight ring
        ctx.beginPath();
        ctx.arc(pt.x, pt.y, 8, 0, Math.PI * 2);
        ctx.fillStyle = 'rgba(0, 245, 212, 0.25)';
        ctx.fill();

        ctx.beginPath();
        ctx.arc(pt.x, pt.y, 5, 0, Math.PI * 2);
        ctx.fillStyle = '#ffffff';
        ctx.shadowColor = '#00f5d4';
        ctx.shadowBlur = 14;
        ctx.fill();
      } else {
        ctx.beginPath();
        ctx.arc(pt.x, pt.y, count > 30 ? 2.5 : 4, 0, Math.PI * 2);
        ctx.fillStyle = '#0a0d18';
        ctx.strokeStyle = '#00f5d4';
        ctx.lineWidth = 2;
        ctx.fill();
        ctx.stroke();
      }
      ctx.restore();
    });

    // Draw X-Axis Baseline & labels
    ctx.beginPath();
    ctx.strokeStyle = 'rgba(255, 255, 255, 0.15)';
    ctx.lineWidth = 1;
    ctx.moveTo(padding.left, padding.top + chartH);
    ctx.lineTo(padding.left + chartW, padding.top + chartH);
    ctx.stroke();

    // X Axis Labels: First, Mid, Last
    ctx.fillStyle = 'rgba(255, 255, 255, 0.45)';
    ctx.font = '10px "Space Grotesk", sans-serif';
    ctx.textBaseline = 'top';

    if (count > 0) {
      ctx.textAlign = 'left';
      ctx.fillText(this.data[0].dateFormatted || 'Run 1', padding.left, padding.top + chartH + 10);

      if (count > 2) {
        const midIdx = Math.floor(count / 2);
        ctx.textAlign = 'center';
        ctx.fillText(this.data[midIdx].dateFormatted || `Run ${midIdx + 1}`, this.points[midIdx].x, padding.top + chartH + 10);
      }

      if (count > 1) {
        ctx.textAlign = 'right';
        ctx.fillText(this.data[count - 1].dateFormatted || `Run ${count}`, padding.left + chartW, padding.top + chartH + 10);
      }
    }
  }

  renderEmptyState(width, height) {
    const ctx = this.ctx;
    ctx.save();
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';

    // Decorative cyber grid crosshairs
    ctx.strokeStyle = 'rgba(255, 255, 255, 0.05)';
    ctx.lineWidth = 1;
    ctx.beginPath();
    ctx.moveTo(width / 2, height / 2 - 40);
    ctx.lineTo(width / 2, height / 2 + 40);
    ctx.moveTo(width / 2 - 40, height / 2);
    ctx.lineTo(width / 2 + 40, height / 2);
    ctx.stroke();

    ctx.fillStyle = 'rgba(255, 255, 255, 0.7)';
    ctx.font = '600 15px "Space Grotesk", sans-serif';
    ctx.fillText('NO SPRINT SESSIONS RECORDED YET', width / 2, height / 2 - 12);

    ctx.fillStyle = 'rgba(255, 255, 255, 0.4)';
    ctx.font = '13px "Space Grotesk", sans-serif';
    ctx.fillText('Play your first game round to visualize your WPM velocity chart over time.', width / 2, height / 2 + 15);

    ctx.restore();
  }

  destroy() {
    this.canvas.removeEventListener('mousemove', this.handleMouseMove);
    this.canvas.removeEventListener('mouseleave', this.handleMouseLeave);
    if (this.resizeObserver) {
      this.resizeObserver.disconnect();
    }
  }
}
