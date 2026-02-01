import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'package:shared_preferences/shared_preferences.dart';
import 'package:intl/intl.dart';
import 'dart:convert';

// © 2026 Scott Leimroth

const String apiBase = 'https://bin-day-brain-proxy.scott-leimroth.workers.dev';
const String weatherApi = 'https://api.open-meteo.com/v1/forecast';
const double wollongongLat = -34.4278;
const double wollongongLon = 150.8931;

void main() {
  runApp(const BinDayBrainApp());
}

class BinDayBrainApp extends StatelessWidget {
  const BinDayBrainApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Bin Day Brain',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(seedColor: Colors.blue),
        useMaterial3: true,
      ),
      home: const MainScreen(),
    );
  }
}

class MainScreen extends StatefulWidget {
  const MainScreen({super.key});

  @override
  State<MainScreen> createState() => _MainScreenState();
}

class _MainScreenState extends State<MainScreen> {
  bool _setupCompleted = false;
  bool _loading = true;

  @override
  void initState() {
    super.initState();
    _checkSetup();
  }

  Future<void> _checkSetup() async {
    final prefs = await SharedPreferences.getInstance();
    setState(() {
      _setupCompleted = prefs.getBool('setup_completed') ?? false;
      _loading = false;
    });
  }

  void _onSetupComplete() {
    setState(() {
      _setupCompleted = true;
    });
  }

  void _onChangeAddress() {
    setState(() {
      _setupCompleted = false;
    });
  }

  @override
  Widget build(BuildContext context) {
    if (_loading) {
      return const Scaffold(
        body: Center(child: CircularProgressIndicator()),
      );
    }

    if (_setupCompleted) {
      return DashboardScreen(onChangeAddress: _onChangeAddress);
    } else {
      return SetupScreen(onComplete: _onSetupComplete);
    }
  }
}

// ==================== SETUP SCREEN ====================

class SetupScreen extends StatefulWidget {
  final VoidCallback onComplete;

  const SetupScreen({super.key, required this.onComplete});

  @override
  State<SetupScreen> createState() => _SetupScreenState();
}

class _SetupScreenState extends State<SetupScreen> {
  List<Map<String, dynamic>> _localities = [];
  List<Map<String, dynamic>> _streets = [];
  List<Map<String, dynamic>> _properties = [];

  Map<String, dynamic>? _selectedLocality;
  Map<String, dynamic>? _selectedStreet;
  Map<String, dynamic>? _selectedProperty;

  String _status = 'Loading suburbs...';
  bool _isLoading = true;

  final _localityController = TextEditingController();
  final _streetController = TextEditingController();
  final _propertyController = TextEditingController();

  @override
  void initState() {
    super.initState();
    _loadLocalities();
  }

  Future<void> _loadLocalities() async {
    try {
      final response = await http.get(Uri.parse('$apiBase/localities.json'));
      if (response.statusCode == 200) {
        final Map<String, dynamic> jsonData = json.decode(response.body);
        final List<dynamic> data = jsonData['localities'] ?? [];
        setState(() {
          _localities = data.cast<Map<String, dynamic>>();
          _localities.sort((a, b) => (a['name'] ?? '').compareTo(b['name'] ?? ''));
          _status = '';
          _isLoading = false;
        });
      }
    } catch (e) {
      setState(() {
        _status = 'Error loading suburbs. Check internet.';
        _isLoading = false;
      });
    }
  }

  Future<void> _loadStreets(int localityId) async {
    setState(() {
      _status = 'Loading streets...';
      _streets = [];
      _properties = [];
      _selectedStreet = null;
      _selectedProperty = null;
      _streetController.clear();
      _propertyController.clear();
    });

    try {
      final response = await http.get(Uri.parse('$apiBase/streets.json?locality=$localityId'));
      if (response.statusCode == 200) {
        final Map<String, dynamic> jsonData = json.decode(response.body);
        final List<dynamic> data = jsonData['streets'] ?? [];
        setState(() {
          _streets = data.cast<Map<String, dynamic>>();
          _streets.sort((a, b) => (a['name'] ?? '').compareTo(b['name'] ?? ''));
          _status = '';
        });
      }
    } catch (e) {
      setState(() => _status = 'Error loading streets.');
    }
  }

  Future<void> _loadProperties(int streetId) async {
    setState(() {
      _status = 'Loading properties...';
      _properties = [];
      _selectedProperty = null;
      _propertyController.clear();
    });

    try {
      final response = await http.get(Uri.parse('$apiBase/properties.json?street=$streetId'));
      if (response.statusCode == 200) {
        final Map<String, dynamic> jsonData = json.decode(response.body);
        final List<dynamic> data = jsonData['properties'] ?? [];
        setState(() {
          _properties = data.cast<Map<String, dynamic>>();
          _properties.sort((a, b) => (a['name'] ?? '').compareTo(b['name'] ?? ''));
          _status = '';
        });
      }
    } catch (e) {
      setState(() => _status = 'Error loading properties.');
    }
  }

  Future<void> _completeSetup() async {
    if (_selectedProperty == null) return;

    final prefs = await SharedPreferences.getInstance();
    await prefs.setInt('property_id', _selectedProperty!['id']);
    await prefs.setBool('setup_completed', true);

    widget.onComplete();
  }

  void _showSelectionSheet(
    String title,
    List<Map<String, dynamic>> items,
    Function(Map<String, dynamic>) onSelected,
  ) {
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
      ),
      builder: (context) => _SelectionSheet(
        title: title,
        items: items,
        onSelected: (item) {
          Navigator.pop(context);
          onSelected(item);
        },
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFFE0E0E0),
      body: SafeArea(
        child: Column(
          children: [
            Expanded(
              child: SingleChildScrollView(
                padding: const EdgeInsets.all(20),
                child: Column(
                  children: [
                    const SizedBox(height: 40),
                    const Text(
                      'Welcome to Bin Day Brain!',
                      style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold),
                      textAlign: TextAlign.center,
                    ),
              const SizedBox(height: 10),
              const Text(
                "Let's find your address for smart bin reminders",
                style: TextStyle(color: Colors.grey),
                textAlign: TextAlign.center,
              ),
              const SizedBox(height: 30),
              Container(
                padding: const EdgeInsets.all(20),
                decoration: BoxDecoration(
                  color: const Color(0xFFD9D9D9),
                  borderRadius: BorderRadius.circular(12),
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Text('Suburb/Locality', style: TextStyle(fontWeight: FontWeight.bold)),
                    const SizedBox(height: 8),
                    GestureDetector(
                      onTap: _isLoading ? null : () => _showSelectionSheet(
                        'Select Suburb',
                        _localities,
                        (item) {
                          setState(() {
                            _selectedLocality = item;
                            _localityController.text = item['name'];
                          });
                          _loadStreets(item['id']);
                        },
                      ),
                      child: Container(
                        padding: const EdgeInsets.symmetric(horizontal: 15, vertical: 12),
                        decoration: BoxDecoration(
                          color: _isLoading ? Colors.grey[300] : Colors.white,
                          borderRadius: BorderRadius.circular(8),
                        ),
                        child: Row(
                          children: [
                            Expanded(
                              child: Text(
                                _selectedLocality?['name'] ?? (_isLoading ? 'Loading...' : 'Tap to select suburb'),
                                style: TextStyle(color: _selectedLocality != null ? Colors.black : Colors.grey),
                              ),
                            ),
                            const Icon(Icons.arrow_drop_down),
                          ],
                        ),
                      ),
                    ),

                    const SizedBox(height: 20),
                    const Text('Street', style: TextStyle(fontWeight: FontWeight.bold)),
                    const SizedBox(height: 8),
                    GestureDetector(
                      onTap: _selectedLocality == null ? null : () => _showSelectionSheet(
                        'Select Street',
                        _streets,
                        (item) {
                          setState(() {
                            _selectedStreet = item;
                            _streetController.text = item['name'];
                          });
                          _loadProperties(item['id']);
                        },
                      ),
                      child: Container(
                        padding: const EdgeInsets.symmetric(horizontal: 15, vertical: 12),
                        decoration: BoxDecoration(
                          color: _selectedLocality == null ? Colors.grey[300] : Colors.white,
                          borderRadius: BorderRadius.circular(8),
                        ),
                        child: Row(
                          children: [
                            Expanded(
                              child: Text(
                                _selectedStreet?['name'] ?? 'Select suburb first',
                                style: TextStyle(color: _selectedStreet != null ? Colors.black : Colors.grey),
                              ),
                            ),
                            const Icon(Icons.arrow_drop_down),
                          ],
                        ),
                      ),
                    ),

                    const SizedBox(height: 20),
                    const Text('Property Number', style: TextStyle(fontWeight: FontWeight.bold)),
                    const SizedBox(height: 8),
                    GestureDetector(
                      onTap: _selectedStreet == null ? null : () => _showSelectionSheet(
                        'Select Property',
                        _properties,
                        (item) {
                          setState(() {
                            _selectedProperty = item;
                            _propertyController.text = item['name'];
                          });
                        },
                      ),
                      child: Container(
                        padding: const EdgeInsets.symmetric(horizontal: 15, vertical: 12),
                        decoration: BoxDecoration(
                          color: _selectedStreet == null ? Colors.grey[300] : Colors.white,
                          borderRadius: BorderRadius.circular(8),
                        ),
                        child: Row(
                          children: [
                            Expanded(
                              child: Text(
                                _selectedProperty?['name'] ?? 'Select street first',
                                style: TextStyle(color: _selectedProperty != null ? Colors.black : Colors.grey),
                              ),
                            ),
                            const Icon(Icons.arrow_drop_down),
                          ],
                        ),
                      ),
                    ),

                    if (_status.isNotEmpty) ...[
                      const SizedBox(height: 15),
                      Text(
                        _status,
                        style: TextStyle(
                          color: _status.contains('Error') ? Colors.red : Colors.grey,
                        ),
                      ),
                    ],
                  ],
                ),
              ),
              const SizedBox(height: 20),
              SizedBox(
                width: double.infinity,
                child: ElevatedButton(
                  onPressed: _selectedProperty != null ? _completeSetup : null,
                  style: ElevatedButton.styleFrom(
                    backgroundColor: Colors.blue,
                    foregroundColor: Colors.white,
                    padding: const EdgeInsets.symmetric(vertical: 15),
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(8),
                    ),
                  ),
                  child: const Text('Complete Setup', style: TextStyle(fontSize: 16)),
                ),
              ),
                  ],
                ),
              ),
            ),
            // Copyright always visible at bottom
            const Padding(
              padding: EdgeInsets.all(10),
              child: Text(
                '© 2026 Scott Leimroth',
                style: TextStyle(color: Colors.grey, fontSize: 11),
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class _SelectionSheet extends StatefulWidget {
  final String title;
  final List<Map<String, dynamic>> items;
  final Function(Map<String, dynamic>) onSelected;

  const _SelectionSheet({
    required this.title,
    required this.items,
    required this.onSelected,
  });

  @override
  State<_SelectionSheet> createState() => _SelectionSheetState();
}

class _SelectionSheetState extends State<_SelectionSheet> {
  List<Map<String, dynamic>> _filtered = [];
  final _searchController = TextEditingController();

  @override
  void initState() {
    super.initState();
    _filtered = widget.items;
  }

  void _filter(String query) {
    setState(() {
      if (query.isEmpty) {
        _filtered = widget.items;
      } else {
        _filtered = widget.items.where((item) =>
          (item['name'] ?? '').toLowerCase().contains(query.toLowerCase())
        ).toList();
      }
    });
  }

  @override
  Widget build(BuildContext context) {
    return DraggableScrollableSheet(
      initialChildSize: 0.7,
      minChildSize: 0.5,
      maxChildSize: 0.95,
      expand: false,
      builder: (context, scrollController) {
        return Container(
          padding: const EdgeInsets.all(20),
          child: Column(
            children: [
              Text(widget.title, style: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
              const SizedBox(height: 15),
              TextField(
                controller: _searchController,
                decoration: InputDecoration(
                  hintText: 'Search...',
                  prefixIcon: const Icon(Icons.search),
                  border: OutlineInputBorder(borderRadius: BorderRadius.circular(10)),
                ),
                onChanged: _filter,
              ),
              const SizedBox(height: 10),
              Expanded(
                child: ListView.builder(
                  controller: scrollController,
                  itemCount: _filtered.length,
                  itemBuilder: (context, index) {
                    final item = _filtered[index];
                    return ListTile(
                      title: Text(item['name'] ?? ''),
                      onTap: () => widget.onSelected(item),
                    );
                  },
                ),
              ),
            ],
          ),
        );
      },
    );
  }
}

// ==================== DASHBOARD SCREEN ====================

class DashboardScreen extends StatefulWidget {
  final VoidCallback onChangeAddress;

  const DashboardScreen({super.key, required this.onChangeAddress});

  @override
  State<DashboardScreen> createState() => _DashboardScreenState();
}

class _DashboardScreenState extends State<DashboardScreen> {
  Map<String, dynamic>? _collectionData;
  String _status = 'Loading...';
  List<String> _alerts = [];
  bool _isRefreshing = false;

  @override
  void initState() {
    super.initState();
    _loadData();
  }

  Future<void> _loadData() async {
    final prefs = await SharedPreferences.getInstance();
    final propertyId = prefs.getInt('property_id');

    if (propertyId == null) return;

    setState(() => _isRefreshing = true);

    try {
      final response = await http.get(Uri.parse('$apiBase/properties/$propertyId.json'));
      if (response.statusCode == 200) {
        final data = json.decode(response.body);

        // If API returns collection_day instead of collections, calculate them
        final collections = data['collections'] as List<dynamic>?;
        if ((collections == null || collections.isEmpty) && data['collection_day'] != null) {
          data['collections'] = _calculateCollections(data['collection_day']);
        }

        setState(() {
          _collectionData = data;
          _status = 'Last updated: ${DateFormat('dd/MM/yyyy HH:mm').format(DateTime.now())}';
        });
        _loadWeather();
      }
    } catch (e) {
      setState(() => _status = 'Error loading data');
    }

    setState(() => _isRefreshing = false);
  }

  List<Map<String, dynamic>> _calculateCollections(int collectionDay) {
    final today = DateTime.now();
    final todayStart = DateTime(today.year, today.month, today.day);

    // Find next occurrence of collection day (API: 1=Mon, Dart: 1=Mon)
    int daysAhead = collectionDay - todayStart.weekday;
    if (daysAhead < 0) daysAhead += 7;

    final nextCollection = todayStart.add(Duration(days: daysAhead));

    // Get ISO week number to determine recycling/landfill week
    final weekNum = _getIsoWeek(nextCollection);
    final isRecyclingWeek = (weekNum % 2 == 0);

    final nextStr = nextCollection.toIso8601String();
    final weekLater = nextCollection.add(const Duration(days: 7));
    final weekLaterStr = weekLater.toIso8601String();

    return [
      {'type': 'FOGO', 'next': {'date': nextStr}},
      {'type': 'Recycling', 'next': {'date': isRecyclingWeek ? nextStr : weekLaterStr}},
      {'type': 'Landfill', 'next': {'date': isRecyclingWeek ? weekLaterStr : nextStr}},
    ];
  }

  int _getIsoWeek(DateTime date) {
    final dayOfYear = date.difference(DateTime(date.year, 1, 1)).inDays;
    return ((dayOfYear - date.weekday + 10) / 7).floor();
  }

  Future<void> _loadWeather() async {
    if (_collectionData == null) return;

    final collections = _collectionData!['collections'] as List<dynamic>?;
    if (collections == null || collections.isEmpty) return;

    DateTime? nearestDate;
    for (var c in collections) {
      final dateStr = c['next']?['date'];
      if (dateStr != null) {
        final date = DateTime.parse(dateStr);
        if (nearestDate == null || date.isBefore(nearestDate)) {
          nearestDate = date;
        }
      }
    }

    if (nearestDate == null) return;

    final daysAhead = nearestDate.difference(DateTime.now()).inDays;
    if (daysAhead < 0 || daysAhead > 7) return;

    try {
      final response = await http.get(Uri.parse(
        '$weatherApi?latitude=$wollongongLat&longitude=$wollongongLon&daily=precipitation_sum,wind_speed_10m_max&timezone=Australia/Sydney&forecast_days=${daysAhead + 1}'
      ));

      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        final daily = data['daily'];
        if (daily != null) {
          final wind = (daily['wind_speed_10m_max'] as List)[daysAhead];
          final rain = (daily['precipitation_sum'] as List)[daysAhead];

          setState(() {
            _alerts = [];
            if (wind >= 40) {
              _alerts.add('Windy (${wind.round()} km/h) - secure your bins!');
            }
            if (rain >= 5) {
              _alerts.add('Rain expected (${rain.round()}mm) - good for FOGO');
            }
          });
        }
      }
    } catch (e) {
      // Weather is optional
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFFE0E0E0),
      body: SafeArea(
        child: Column(
          children: [
            Expanded(
              child: RefreshIndicator(
                onRefresh: _loadData,
                child: SingleChildScrollView(
                  physics: const AlwaysScrollableScrollPhysics(),
                  padding: const EdgeInsets.all(20),
                  child: Column(
                    children: [
                      const Text(
                        'Bin Day Brain',
                        style: TextStyle(fontSize: 28, fontWeight: FontWeight.bold),
                      ),
                      const Text(
                        'Wollongong Smart Bin Reminders',
                        style: TextStyle(color: Colors.grey),
                      ),
                      const SizedBox(height: 20),

                      // Alerts
                      ..._alerts.map((alert) => Container(
                        width: double.infinity,
                        margin: const EdgeInsets.only(bottom: 10),
                        padding: const EdgeInsets.all(12),
                        decoration: BoxDecoration(
                          color: alert.contains('Windy') ? Colors.orange[700] : Colors.blue,
                          borderRadius: BorderRadius.circular(8),
                        ),
                        child: Text(
                          alert,
                          style: const TextStyle(color: Colors.white),
                          textAlign: TextAlign.center,
                        ),
                      )),

                      const SizedBox(height: 10),

                      // Bin Cards
                      _buildBinCards(),

                      const SizedBox(height: 10),
                      Text(_status, style: const TextStyle(color: Colors.grey, fontSize: 12)),
                      const SizedBox(height: 20),

                      // Buttons
                      Wrap(
                        spacing: 10,
                        runSpacing: 10,
                        alignment: WrapAlignment.center,
                        children: [
                          ElevatedButton(
                            onPressed: widget.onChangeAddress,
                            style: ElevatedButton.styleFrom(backgroundColor: Colors.grey[700]),
                            child: const Text('Change Address', style: TextStyle(color: Colors.white)),
                          ),
                          ElevatedButton(
                            onPressed: () => _showWhichBinDialog(context),
                            style: ElevatedButton.styleFrom(backgroundColor: Colors.purple),
                            child: const Text('Which Bin?', style: TextStyle(color: Colors.white)),
                          ),
                          ElevatedButton(
                            onPressed: _isRefreshing ? null : _loadData,
                            child: const Text('Refresh'),
                          ),
                        ],
                      ),
                    ],
                  ),
                ),
              ),
            ),
            // Copyright always visible at bottom
            const Padding(
              padding: EdgeInsets.all(10),
              child: Text(
                '© 2026 Scott Leimroth',
                style: TextStyle(color: Colors.grey, fontSize: 11),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildBinCards() {
    final collections = _collectionData?['collections'] as List<dynamic>? ?? [];

    Map<String, Map<String, dynamic>> binData = {};
    for (var c in collections) {
      final type = (c['type'] ?? '').toString().toLowerCase();
      final dateStr = c['next']?['date'];

      String binType;
      if (type.contains('fogo') || type.contains('organic')) {
        binType = 'fogo';
      } else if (type.contains('recycling')) {
        binType = 'recycling';
      } else if (type.contains('landfill') || type.contains('garbage') || type.contains('waste')) {
        binType = 'landfill';
      } else {
        continue;
      }

      if (dateStr != null) {
        binData[binType] = {'date': DateTime.parse(dateStr)};
      }
    }

    return Column(
      children: [
        Row(
          children: [
            Expanded(child: _buildBinCard('FOGO', const Color(0xFF2D7F2D), binData['fogo']?['date'])),
            const SizedBox(width: 10),
            Expanded(child: _buildBinCard('Recycling', const Color(0xFFD4A500), binData['recycling']?['date'])),
          ],
        ),
        const SizedBox(height: 10),
        _buildBinCard('Landfill', const Color(0xFFC92A2A), binData['landfill']?['date']),
      ],
    );
  }

  Widget _buildBinCard(String title, Color color, DateTime? date) {
    int days = 0;
    String dateStr = '';

    if (date != null) {
      final now = DateTime.now();
      final today = DateTime(now.year, now.month, now.day);
      final collectionDay = DateTime(date.year, date.month, date.day);
      days = collectionDay.difference(today).inDays;
      dateStr = DateFormat('dd MMMM yyyy').format(date);
    }

    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: color,
        borderRadius: BorderRadius.circular(12),
      ),
      child: Column(
        children: [
          Text(title, style: const TextStyle(color: Colors.white, fontSize: 20, fontWeight: FontWeight.bold)),
          const SizedBox(height: 15),
          Text(
            date != null ? '$days' : '--',
            style: const TextStyle(color: Colors.white, fontSize: 48, fontWeight: FontWeight.bold),
          ),
          Text(
            days == 1 ? 'day until collection' : 'days until collection',
            style: const TextStyle(color: Colors.white70, fontSize: 12),
          ),
          const SizedBox(height: 10),
          Text(dateStr, style: const TextStyle(color: Colors.white70, fontSize: 12)),
        ],
      ),
    );
  }

  void _showWhichBinDialog(BuildContext context) {
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
      ),
      builder: (context) => const WhichBinSheet(),
    );
  }
}

// ==================== WHICH BIN SHEET ====================

class WhichBinSheet extends StatefulWidget {
  const WhichBinSheet({super.key});

  @override
  State<WhichBinSheet> createState() => _WhichBinSheetState();
}

class _WhichBinSheetState extends State<WhichBinSheet> {
  List<Map<String, dynamic>> _materials = [];
  List<Map<String, dynamic>> _filtered = [];
  bool _loading = true;
  final _searchController = TextEditingController();

  @override
  void initState() {
    super.initState();
    _loadMaterials();
  }

  Future<void> _loadMaterials() async {
    try {
      final response = await http.get(Uri.parse('$apiBase/materials.json'));
      if (response.statusCode == 200) {
        final Map<String, dynamic> jsonData = json.decode(response.body);
        final List<dynamic> data = jsonData['materials'] ?? [];
        setState(() {
          _materials = data.cast<Map<String, dynamic>>();
          _materials.sort((a, b) => (a['title'] ?? '').compareTo(b['title'] ?? ''));
          _filtered = _materials;
          _loading = false;
        });
      }
    } catch (e) {
      setState(() => _loading = false);
    }
  }

  void _filter(String query) {
    setState(() {
      if (query.isEmpty) {
        _filtered = _materials;
      } else {
        _filtered = _materials.where((m) =>
          (m['title'] ?? '').toLowerCase().contains(query.toLowerCase())
        ).toList();
      }
    });
  }

  Color _getBinColor(String? disposal) {
    switch (disposal?.toLowerCase()) {
      case 'recycle':
      case 'recycling':
        return const Color(0xFFD4A500); // Yellow
      case 'organic':
      case 'fogo':
        return const Color(0xFF2D7F2D); // Green
      case 'waste':
      case 'landfill':
      case 'garbage':
        return const Color(0xFFC92A2A); // Red
      case 'crc':
        return const Color(0xFF1E88E5); // Blue
      case 'special':
        return const Color(0xFFFF6F00); // Orange
      case 'clean_up':
        return const Color(0xFF7B1FA2); // Purple
      default:
        return const Color(0xFFC92A2A); // Default to red (waste)
    }
  }

  String _getBinName(String? disposal) {
    switch (disposal?.toLowerCase()) {
      case 'recycle':
      case 'recycling':
        return 'Yellow Recycling Bin';
      case 'organic':
      case 'fogo':
        return 'Green FOGO Bin';
      case 'waste':
      case 'landfill':
      case 'garbage':
        return 'Red Landfill Bin';
      case 'crc':
        return 'Community Recycling Centre';
      case 'special':
        return 'Special Disposal';
      case 'clean_up':
        return 'Council Clean-up';
      default:
        return 'Red Landfill Bin';
    }
  }

  @override
  Widget build(BuildContext context) {
    return DraggableScrollableSheet(
      initialChildSize: 0.9,
      minChildSize: 0.5,
      maxChildSize: 0.95,
      expand: false,
      builder: (context, scrollController) {
        return Container(
          padding: const EdgeInsets.all(20),
          child: Column(
            children: [
              const Text(
                'Which Bin Does It Go In?',
                style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
              ),
              const SizedBox(height: 15),
              TextField(
                controller: _searchController,
                decoration: InputDecoration(
                  hintText: 'Search for an item...',
                  prefixIcon: const Icon(Icons.search),
                  border: OutlineInputBorder(borderRadius: BorderRadius.circular(10)),
                ),
                onChanged: _filter,
              ),
              const SizedBox(height: 10),
              Text('${_filtered.length} items', style: const TextStyle(color: Colors.grey)),
              const SizedBox(height: 10),
              Expanded(
                child: _loading
                  ? const Center(child: CircularProgressIndicator())
                  : ListView.builder(
                      controller: scrollController,
                      itemCount: _filtered.length,
                      itemBuilder: (context, index) {
                        final item = _filtered[index];
                        // Try both field names - API might use either
                        final disposal = item['disposal'] ?? item['bin_type'] ?? 'waste';
                        return Container(
                          margin: const EdgeInsets.only(bottom: 8),
                          padding: const EdgeInsets.all(12),
                          decoration: BoxDecoration(
                            color: _getBinColor(disposal),
                            borderRadius: BorderRadius.circular(8),
                          ),
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Text(
                                item['title'] ?? 'Unknown',
                                style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold),
                              ),
                              Text(
                                _getBinName(disposal),
                                style: const TextStyle(color: Colors.white70, fontSize: 12),
                              ),
                              if (item['tip'] != null)
                                Text(
                                  item['tip'],
                                  style: const TextStyle(color: Colors.white70, fontSize: 11),
                                ),
                            ],
                          ),
                        );
                      },
                    ),
              ),
            ],
          ),
        );
      },
    );
  }
}
