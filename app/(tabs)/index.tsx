import { useEffect, useState } from 'react';
import { ActivityIndicator, ScrollView, StyleSheet, Text, View } from 'react-native';

import { API_BASE_URL } from '@/constants/api';
const API_URL = `${API_BASE_URL}/api/trip/latest/`;

type Event = {
  id: number;
  timestamp: string;
  severity: 'low' | 'medium' | 'high';
  duration: number;
};

type Trip = {
  id: number;
  start_time: string;
  end_time: string;
  duration: string;
  events: Event[];
};

const severityColor = (severity: string) => {
  if (severity === 'high') return '#FF3B30';
  if (severity === 'medium') return '#FF9500';
  return '#FFD60A';
};

const severityBg = (severity: string) => {
  if (severity === 'high') return '#2C1010';
  if (severity === 'medium') return '#2C1E00';
  return '#2C2600';
};

const formatTime = (iso: string) => {
  const date = new Date(iso);
  return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
};

const formatDate = (iso: string) => {
  const date = new Date(iso);
  return date.toLocaleDateString([], { weekday: 'long', day: 'numeric', month: 'long', year: 'numeric' });
};

export default function HomeScreen() {
  const [trip, setTrip] = useState<Trip | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetch(API_URL)
      .then(res => {
        if (!res.ok) throw new Error('No trips recorded yet');
        return res.json();
      })
      .then(data => {
        setTrip(data);
        setLoading(false);
      })
      .catch(err => {
        setError(err.message);
        setLoading(false);
      });
  }, []);

  if (loading) {
    return (
      <View style={styles.centered}>
        <ActivityIndicator size="large" color="white" />
        <Text style={styles.loadingText}>Fetching trip data...</Text>
      </View>
    );
  }

  if (error || !trip) {
    return (
      <View style={styles.centered}>
        <Text style={styles.errorEmoji}>🚗</Text>
        <Text style={styles.errorText}>No trips recorded yet</Text>
        <Text style={styles.errorSub}>Complete a drive to see your summary</Text>
      </View>
    );
  }

  const severityCounts = { low: 0, medium: 0, high: 0 };
  trip.events.forEach(e => severityCounts[e.severity]++);

  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.content}>

      <Text style={styles.heading}>RoadGuard</Text>
      <Text style={styles.subheading}>Latest Trip Summary</Text>

      {/* Trip Info Card */}
      <View style={styles.card}>
        <Text style={styles.cardTitle}>📅  {formatDate(trip.start_time)}</Text>
        <View style={styles.row}>
          <View style={styles.infoBlock}>
            <Text style={styles.infoLabel}>Start</Text>
            <Text style={styles.infoValue}>{formatTime(trip.start_time)}</Text>
          </View>
          <View style={styles.infoBlock}>
            <Text style={styles.infoLabel}>End</Text>
            <Text style={styles.infoValue}>{formatTime(trip.end_time)}</Text>
          </View>
          <View style={styles.infoBlock}>
            <Text style={styles.infoLabel}>Duration</Text>
            <Text style={styles.infoValue}>{trip.duration}</Text>
          </View>
        </View>
      </View>

      {/* Events Summary Card */}
      <View style={styles.card}>
        <Text style={styles.cardTitle}>⚠️  Drowsiness Events</Text>
        <Text style={styles.bigNumber}>{trip.events.length}</Text>
        <View style={styles.row}>
          {(['low', 'medium', 'high'] as const).map(s => (
            <View key={s} style={[styles.pill, { borderColor: severityColor(s), backgroundColor: severityBg(s) }]}>
              <Text style={[styles.pillText, { color: severityColor(s) }]}>
                {severityCounts[s]} {s.charAt(0).toUpperCase() + s.slice(1)}
              </Text>
            </View>
          ))}
        </View>
      </View>

      {/* Timeline */}
      <View style={styles.card}>
        <Text style={styles.cardTitle}>🕐  Event Timeline</Text>
        {trip.events.map((event) => (
          <View key={event.id} style={styles.timelineItem}>
            <View style={[styles.timelineDot, { backgroundColor: severityColor(event.severity) }]} />
            <View style={styles.timelineContent}>
              <Text style={styles.timelineTime}>{formatTime(event.timestamp)}</Text>
              <Text style={styles.timelineDesc}>Eyes closed for {event.duration}s</Text>
              <View style={[styles.pill, { borderColor: severityColor(event.severity), backgroundColor: severityBg(event.severity) }]}>
                <Text style={[styles.pillText, { color: severityColor(event.severity) }]}>
                  {event.severity.charAt(0).toUpperCase() + event.severity.slice(1)}
                </Text>
              </View>
            </View>
          </View>
        ))}
      </View>

    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#0D0D0D',
  },
  content: {
    padding: 20,
    paddingTop: 60,
    gap: 16,
  },
  centered: {
    flex: 1,
    backgroundColor: '#0D0D0D',
    justifyContent: 'center',
    alignItems: 'center',
    gap: 12,
  },
  heading: {
    fontSize: 28,
    fontWeight: 'bold',
    color: 'white',
  },
  subheading: {
    fontSize: 14,
    color: '#888',
    marginBottom: 8,
  },
  card: {
    backgroundColor: '#1C1C1E',
    borderRadius: 16,
    padding: 20,
    gap: 12,
  },
  cardTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#AEAEB2',
  },
  row: {
    flexDirection: 'row',
    gap: 12,
  },
  infoBlock: {
    flex: 1,
    alignItems: 'center',
    backgroundColor: '#2C2C2E',
    borderRadius: 12,
    padding: 12,
  },
  infoLabel: {
    fontSize: 12,
    color: '#888',
    marginBottom: 4,
  },
  infoValue: {
    fontSize: 16,
    fontWeight: '600',
    color: 'white',
  },
  bigNumber: {
    fontSize: 56,
    fontWeight: 'bold',
    color: 'white',
  },
  pill: {
    borderWidth: 1,
    borderRadius: 20,
    paddingHorizontal: 12,
    paddingVertical: 4,
    alignSelf: 'flex-start',
  },
  pillText: {
    fontSize: 13,
    fontWeight: '600',
  },
  timelineItem: {
    flexDirection: 'row',
    gap: 12,
    alignItems: 'flex-start',
  },
  timelineDot: {
    width: 12,
    height: 12,
    borderRadius: 6,
    marginTop: 4,
  },
  timelineContent: {
    flex: 1,
    gap: 6,
  },
  timelineTime: {
    fontSize: 14,
    fontWeight: '600',
    color: 'white',
  },
  timelineDesc: {
    fontSize: 13,
    color: '#888',
  },
  loadingText: {
    color: '#888',
    marginTop: 12,
  },
  errorEmoji: {
    fontSize: 60,
  },
  errorText: {
    fontSize: 20,
    fontWeight: 'bold',
    color: 'white',
  },
  errorSub: {
    fontSize: 14,
    color: '#888',
  },
});