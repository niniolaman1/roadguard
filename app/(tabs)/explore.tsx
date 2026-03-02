import { useEffect, useState } from 'react';
import { ActivityIndicator, FlatList, StyleSheet, Text, TouchableOpacity, View } from 'react-native';

const API_URL = 'https://nonsuppressed-marybelle-sleekly.ngrok-free.dev/api/trips/';

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

const severityColor = (s: string) => s === 'high' ? '#FF3B30' : s === 'medium' ? '#FF9500' : '#FFD60A';
const formatTime = (iso: string) => new Date(iso).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
const formatDate = (iso: string) => new Date(iso).toLocaleDateString([], { weekday: 'short', day: 'numeric', month: 'short', year: 'numeric' });

export default function HistoryScreen() {
  const [trips, setTrips] = useState<Trip[]>([]);
  const [loading, setLoading] = useState(true);
  const [selected, setSelected] = useState<Trip | null>(null);

  useEffect(() => {
    fetch(API_URL)
      .then(res => res.json())
      .then(data => {
        setTrips(data);
        setLoading(false);
      })
      .catch(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <View style={styles.centered}>
        <ActivityIndicator size="large" color="white" />
      </View>
    );
  }

  if (selected) {
    const counts = { low: 0, medium: 0, high: 0 };
    selected.events.forEach(e => counts[e.severity]++);

    return (
      <View style={styles.container}>
        <TouchableOpacity onPress={() => setSelected(null)} style={styles.backButton}>
          <Text style={styles.backText}>← Back to History</Text>
        </TouchableOpacity>

        <FlatList
          contentContainerStyle={styles.content}
          data={selected.events}
          keyExtractor={item => item.id.toString()}
          ListHeaderComponent={
            <>
              <Text style={styles.heading}>Trip Detail</Text>
              <View style={styles.card}>
                <Text style={styles.cardTitle}>📅  {formatDate(selected.start_time)}</Text>
                <View style={styles.row}>
                  {[['Start', formatTime(selected.start_time)], ['End', formatTime(selected.end_time)], ['Duration', selected.duration]].map(([label, value]) => (
                    <View key={label} style={styles.infoBlock}>
                      <Text style={styles.infoLabel}>{label}</Text>
                      <Text style={styles.infoValue}>{value}</Text>
                    </View>
                  ))}
                </View>
              </View>

              <View style={styles.card}>
                <Text style={styles.cardTitle}>⚠️  Drowsiness Events</Text>
                <Text style={styles.bigNumber}>{selected.events.length}</Text>
                <View style={styles.row}>
                  {(['low', 'medium', 'high'] as const).map(s => (
                    <View key={s} style={[styles.pill, { borderColor: severityColor(s) }]}>
                      <Text style={[styles.pillText, { color: severityColor(s) }]}>
                        {counts[s]} {s.charAt(0).toUpperCase() + s.slice(1)}
                      </Text>
                    </View>
                  ))}
                </View>
              </View>
              <Text style={styles.cardTitle}>🕐  Event Timeline</Text>
            </>
          }
          ListEmptyComponent={<Text style={styles.mutedText}>No events this trip</Text>}
          renderItem={({ item }) => (
            <View style={styles.timelineItem}>
              <View style={[styles.dot, { backgroundColor: severityColor(item.severity) }]} />
              <View style={{ flex: 1, gap: 4 }}>
                <Text style={styles.infoValue}>{formatTime(item.timestamp)}</Text>
                <Text style={styles.mutedText}>Eyes closed for {item.duration}s</Text>
                <View style={[styles.pill, { borderColor: severityColor(item.severity) }]}>
                  <Text style={[styles.pillText, { color: severityColor(item.severity) }]}>
                    {item.severity.charAt(0).toUpperCase() + item.severity.slice(1)}
                  </Text>
                </View>
              </View>
            </View>
          )}
        />
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <FlatList
        contentContainerStyle={styles.content}
        data={trips}
        keyExtractor={item => item.id.toString()}
        ListHeaderComponent={
          <>
            <Text style={styles.heading}>RoadGuard</Text>
            <Text style={styles.subheading}>Trip History</Text>
          </>
        }
        ListEmptyComponent={
          <View style={styles.centered}>
            <Text style={{ fontSize: 60 }}>🚗</Text>
            <Text style={styles.boldWhite}>No trips recorded yet</Text>
          </View>
        }
        renderItem={({ item }) => (
          <TouchableOpacity style={styles.tripCard} onPress={() => setSelected(item)}>
            <View style={{ flex: 1 }}>
              <Text style={styles.infoValue}>{formatDate(item.start_time)}</Text>
              <Text style={styles.mutedText}>{formatTime(item.start_time)} → {formatTime(item.end_time)}  ·  {item.duration}</Text>
            </View>
            <View style={styles.eventBadge}>
              <Text style={styles.eventBadgeText}>{item.events.length} events</Text>
            </View>
          </TouchableOpacity>
        )}
      />
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#0D0D0D' },
  content: { padding: 20, paddingTop: 60, gap: 12 },
  centered: { flex: 1, backgroundColor: '#0D0D0D', justifyContent: 'center', alignItems: 'center', gap: 12 },
  heading: { fontSize: 28, fontWeight: 'bold', color: 'white', marginBottom: 4 },
  subheading: { fontSize: 14, color: '#888', marginBottom: 8 },
  boldWhite: { fontSize: 20, fontWeight: 'bold', color: 'white' },
  mutedText: { fontSize: 13, color: '#888' },
  card: { backgroundColor: '#1C1C1E', borderRadius: 16, padding: 20, gap: 12, marginBottom: 12 },
  cardTitle: { fontSize: 16, fontWeight: '600', color: '#AEAEB2', marginBottom: 8 },
  row: { flexDirection: 'row', gap: 12 },
  infoBlock: { flex: 1, alignItems: 'center', backgroundColor: '#2C2C2E', borderRadius: 12, padding: 12 },
  infoLabel: { fontSize: 12, color: '#888', marginBottom: 4 },
  infoValue: { fontSize: 16, fontWeight: '600', color: 'white' },
  bigNumber: { fontSize: 56, fontWeight: 'bold', color: 'white' },
  pill: { borderWidth: 1, borderRadius: 20, paddingHorizontal: 12, paddingVertical: 4, alignSelf: 'flex-start' },
  pillText: { fontSize: 13, fontWeight: '600' },
  timelineItem: { flexDirection: 'row', gap: 12, alignItems: 'flex-start', marginBottom: 16 },
  dot: { width: 12, height: 12, borderRadius: 6, marginTop: 4 },
  tripCard: { backgroundColor: '#1C1C1E', borderRadius: 16, padding: 16, flexDirection: 'row', alignItems: 'center' },
  eventBadge: { backgroundColor: '#2C2C2E', borderRadius: 12, paddingHorizontal: 12, paddingVertical: 6 },
  eventBadgeText: { color: '#888', fontSize: 13, fontWeight: '600' },
  backButton: { paddingHorizontal: 20, paddingTop: 60, paddingBottom: 12 },
  backText: { color: '#007AFF', fontSize: 16 },
});
