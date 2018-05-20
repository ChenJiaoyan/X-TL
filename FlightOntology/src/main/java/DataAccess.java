import java.sql.*;
import java.util.ArrayList;
import java.util.HashMap;

public class DataAccess {

    private Connection conn = null;
    private Statement stmt = null;
    private String dep_att_s = null;
    private String met_att_s = null;

    public DataAccess() throws SQLException {
        conn = DriverManager.getConnection("jdbc:mysql://116.62.18.214/flight?user=jiaoyan&password=123456");
        stmt = conn.createStatement();
        dep_att_s = "Carrier,Origin,Dest,FlightNum,FlightDate,CRSDepTime,DepDelay,CRSArrTime,ArrDelay,CarrierDelay,WeatherDelay," +
                "NASDelay,SecurityDelay,LateAircraftDelay,Distance,DistanceGroup,ArrivalDelayGroups,DepartureDelayGroups," +
                "OriginCityName,DestCityName";
        met_att_s = "temperature,dewPoint,visibility,humidity,cloudCover,pressure,windSpeed,windBearing,precipType,summary";
    }


    /**
     * read target departure-related data
     *
     * @param y
     * @param car
     * @param ori
     * @param des
     * @param CRS_dep_t1
     * @param CRS_dep_t2
     * @return
     * @throws SQLException
     */
    public ArrayList<HashMap<String, String>> getTargetDep(int y, String car, String ori, String des, String CRS_dep_t1, String CRS_dep_t2) throws SQLException {
        ArrayList<HashMap<String, String>> results = new ArrayList<>();
        String sql_s = String.format("select %s " + "from flight.flight_%d where Carrier='%s' and Origin='%s' and Dest='%s' and " +
                "CRSDepTime >= '%s' and CRSDepTime <= '%s' order by FlightDate,CRSDepTime", dep_att_s, y, car, ori, des, CRS_dep_t1, CRS_dep_t2);
        System.out.printf("sql query for %d\n", y);
        ResultSet rs = stmt.executeQuery(sql_s);
        while (rs.next()) {
            HashMap<String, String> res = new HashMap<>();
            for (String att : dep_att_s.split(",")) {
                res.put(att, rs.getString(att));
            }
            results.add(res);
        }
        rs.close();
        return results;
    }


    /**
     * read mete data of airport
     *
     * @param apt
     * @param cut_t
     * @return
     * @throws SQLException
     */
    HashMap<String, HashMap<String, String>> getMete(String apt, String cut_t) throws SQLException {
        String sql_s = String.format("select * from flight.mete where airport = '%s' and hour like '____-__-__T%s' order by hour",
                apt, cut_t.substring(0, 2));
        System.out.printf("sql query \n");
        ResultSet rs = stmt.executeQuery(sql_s);
        HashMap<String, HashMap<String, String>> d_met = new HashMap<>();
        while (rs.next()) {
            HashMap<String, String> res = new HashMap<>();
            for (String att : met_att_s.split(",")) {
                res.put(att, rs.getString(att));
            }
            d_met.put(rs.getString("hour").substring(0, 10), res);
        }
        rs.close();
        return d_met;
    }

    /**
     * recent N departures at an airport
     *
     * @param y
     * @param N
     * @param apt
     * @param cut_t
     * @return
     */
    HashMap<String, ArrayList<HashMap<String, String>>> getAptRec(int y, int N, String apt, String cut_t) throws SQLException {
        String sql_s = String.format("select %s from flight.flight_%d " +
                "where Origin='%s' and CRSDepTime<='%s' and CRSDepTime > '%02d00' " +
                "order by FlightDate,CRSDepTime desc", dep_att_s, y, apt, cut_t, Integer.parseInt(cut_t.substring(0, 2)) - 3);
        System.out.printf("sql query for %d\n", y);
        return recDep(sql_s, N);
    }


    /**
     * recent N departures of a carrier
     *
     * @param y
     * @param N
     * @param car
     * @param cut_t
     * @return
     * @throws SQLException
     */
    HashMap<String, ArrayList<HashMap<String, String>>> getCarRec(int y, int N, String car, String cut_t) throws SQLException {
        String sql_s = String.format("select %s from flight.flight_%d " +
                "where Carrier='%s' and CRSDepTime<='%s' and CRSDepTime > '%02d00' " +
                "order by FlightDate,CRSDepTime desc", dep_att_s, y, car, cut_t, Integer.parseInt(cut_t.substring(0, 2)) - 3);
        System.out.printf("sql query for %d\n", y);
        return recDep(sql_s, N);
    }

    /**
     * recent N departure of a carrier at an airport
     *
     * @param y
     * @param N
     * @param car
     * @param apt
     * @param cut_t
     * @return
     * @throws SQLException
     */
    HashMap<String, ArrayList<HashMap<String, String>>> getCarAptRec(int y, int N, String car, String apt, String cut_t) throws SQLException {
        String sql_s = String.format("select %s from flight.flight_%d " +
                        "where Origin='%s' and Carrier='%s' and CRSDepTime<='%s' order by FlightDate,CRSDepTime desc",
                dep_att_s, y, apt, car, cut_t);
        System.out.printf("sql query for %d\n", y);
        return recDep(sql_s, N);
    }


    /**
     * get recent departures
     *
     * @param sql_s
     * @param rec_num
     * @return
     * @throws SQLException
     */
    private HashMap<String, ArrayList<HashMap<String, String>>> recDep(String sql_s, int rec_num) throws SQLException {
        HashMap<String, ArrayList<HashMap<String, String>>> d_dep = new HashMap<>();
        ResultSet rs = stmt.executeQuery(sql_s);
        while (rs.next()) {
            String k = rs.getString("FlightDate").substring(0, 10);
            if (!d_dep.containsKey(k)) {
                HashMap<String, String> dep = new HashMap<>();
                for (String att : dep_att_s.split(",")) {
                    dep.put(att, rs.getString(att));
                }
                ArrayList<HashMap<String, String>> deps = new ArrayList<>();
                deps.add(dep);
                d_dep.put(k, deps);
            } else {
                if (d_dep.get(k).size() < rec_num) {
                    HashMap<String, String> dep = new HashMap<>();
                    for (String att : dep_att_s.split(",")) {
                        dep.put(att, rs.getString(att));
                    }
                    d_dep.get(k).add(dep);
                }
            }
        }
        return d_dep;
    }

    /**
     * close database connection
     *
     * @throws SQLException
     */
    void close() throws SQLException {
        if (stmt != null) {
            stmt.close();
        }
        if (conn != null) {
            conn.close();
        }
    }
}
